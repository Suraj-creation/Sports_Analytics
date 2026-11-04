"""Names and singles format never bind initial visual near/far slots to athletes.

IndiaDEV diagnostic: named P1=Lakshya Sen, P2=Loh Kean Yew; near red is Loh.
These controlled first-view observations reproduce that configuration without
media/models or a tracker reset. Geometry is evidence, never identity review.
"""
from types import SimpleNamespace
import numpy as np
import pytest
from bai_badminton.analytics.individual import build_individual_analytics
from bai_badminton.court import Homography
from bai_badminton.engine import BadmintonMatchEngine,EngineConfig
from bai_badminton.events.stroke import StrokePrediction
from bai_badminton.events.contact import ContactCandidate
from bai_badminton.identity_review import IdentityReviewLedger
from bai_badminton.participant_geometry import GeometryBracketPolicy
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception_types import ChunkPerception,FramePerception,PersonObs
from bai_badminton.plugin import BadmintonSession
from bai_badminton.rules import MatchConfig
from bai_engine.config import ModelChoice,Profile
from bai_engine.schema import Event,EventStatus,Provenance,TrackObject
from bai_engine.schema.session import Session,Source,SourceKind,MediaInfo,PlayerInfo,ParticipantInfo,ParticipantRoster
from bai_engine.store import EventStore

NAMES={'P1':'Lakshya Sen','P2':'Loh Kean Yew'}
H=np.array([[97.64691427896608,29.810278013941463,627.5530554541201],[1.0391423266292708,-5.920500226904281,402.6253397669846],[.0014413582116471692,.048556459491497,1.]])

class CaptureClassifier:
    name='controlled-context-capture'
    def __init__(self):self.contexts=[]
    def predict(self,context):
        self.contexts.append(context)
        return StrokePrediction({'unknown':0.},self.name)

def setup(tmp_path,*,skipped=False,bracket=False):
    store=EventStore(tmp_path/'events.sqlite','S1');capture=CaptureClassifier()
    policy=GeometryBracketPolicy()if bracket else None
    engine=BadmintonMatchEngine('S1',EngineConfig(fps=30,frame_width=1280,frame_height=720,match=MatchConfig(discipline='singles'),participant_geometry_policy=policy),store,stroke_classifier=capture,player_names=NAMES)
    engine.set_calibration(0,Homography(H,0.,12),emit=False)
    engine._provenance['player_detector']='controlled-detections'
    frames=[]
    for frame in range(17):
        fresh=not(skipped and frame==8)
        near=np.zeros((17,3));near[[9,10]]=[795,395,.95]
        far=np.zeros((17,3));far[[9,10]]=[735,230,.95]
        people=[PersonObs(2,np.array([631.,369.,829.,545.]),.95,kps=near if fresh else None,court_xy=(.8,-4.4),detector_matched=fresh),PersonObs(1,np.array([708.,175.,764.,295.]),.95,kps=far if fresh else None,court_xy=(1.4,5.2),detector_matched=fresh)]
        frames.append(FramePerception(frame_idx=frame,shuttle_xy=(795.-12*abs(frame-8),395.),shuttle_conf=.95,persons=people,shot_id=0,view='main',calibration_state=CalibrationState.VALID,detector_observed=fresh,pose_stride=1))
    engine.ingest(ChunkPerception(0,16,frames))
    # No real or synthetic reset may explain away initial identity uncertainty.
    assert all(event.payload.get('reason')not in {'visual_tracker_reset','calibration_changed','prolonged_coverage_loss'}for event in store.query(types=['identity_ambiguity']))
    # The contact provider supplies an anonymous episode, exactly as the real
    # detector does before the engine maps it to a named slot. This isolates
    # identity from contact-peak timing and preserves the real ingest buffers.
    episode=next(key for key,value in engine._participant_frames[8].items()if value.track_id==2)
    candidate=ContactCandidate(frame=8,player_id=episode,p=.9,shuttle_xy=(795.,395.),scores={'proximity':1.},attribution_reason='controlled_episode_hypothesis')
    engine.contact_inference=SimpleNamespace(detect=lambda window,**options:[candidate])
    engine._advance(8)
    contacts=[c for c in engine._open_contacts if c.cand.frame==8]
    assert len(contacts)==1,'controlled turn must reach the real contact/slot boundary'
    return engine,store,capture,contacts[0]

def classify(engine,store,capture,item):
    engine._classify(item,next_frame=15,is_serve=False,receiver=None)
    return store.query(types=['stroke'])[0],capture.contexts[-1]

def official_fixture(store,stroke):
    store.append(Event(session_id='S1',type='rally_end',frame_start=0,frame_end=16,pts_us=0,status=EventStatus.CONFIRMED,payload={'official':True,'shots':[{'event_id':stroke.event_id,'frame':8}]},provenance=Provenance(model='controlled-official-rally')))

def roster():
    return ParticipantRoster(match_format='singles',participants=[ParticipantInfo(participant_id='sen',name=NAMES['P1']),ParticipantInfo(participant_id='loh',name=NAMES['P2'])])

def test_initial_format_and_scoring_names_do_not_name_the_near_contact(tmp_path):
    engine,store,capture,item=setup(tmp_path)
    assert item.cand.player_id is None and item.event.actors.player_id is None
    stroke,context=classify(engine,store,capture,item)
    assert stroke.actors.player_id is None and context.player_id is None
    assert stroke.payload.get('classification_context_source')!='named_player'
    official_fixture(store,stroke)
    totals=build_individual_analytics(store,roster(),max_frame=16,fps=30)
    assert totals['accounting']=={'total_shots':1,'attributed_shots':0,'unattributed_shots':1}
    assert not store.query(types=['point'])

def test_initial_visual_player_tracks_keep_names_unresolved(tmp_path):
    engine,_,_,_=setup(tmp_path)
    tracks=[sample for sample in engine.drain_tracks()if sample.obj==TrackObject.PLAYER and sample.visible]
    assert tracks
    assert all(sample.player_id is None for sample in tracks)
    assert {sample.track_id for sample in tracks}=={1,2}

def test_fresh_anonymous_geometry_remains_available_without_named_binding(tmp_path):
    engine,store,capture,item=setup(tmp_path)
    assert item.event.payload.get('participant_hypothesis',{}).get('status')=='provisional'
    stroke,context=classify(engine,store,capture,item)
    assert context.player_id is None
    assert context.hitter_court_xy==pytest.approx((.8,-4.4))
    assert stroke.payload['classification_context_source']=='provisional_track_episode'

@pytest.mark.parametrize('bracket',[False,True])
def test_skipped_detector_cannot_be_used_as_a_named_observation(tmp_path,bracket):
    engine,store,capture,item=setup(tmp_path,skipped=True,bracket=bracket)
    assert item.event.actors.player_id is None and item.cand.player_id is None
    stroke,context=classify(engine,store,capture,item)
    assert stroke.actors.player_id is None and context.player_id is None
    assert context.contact_above_head is None
    if bracket:
        assert context.hitter_court_xy==pytest.approx((.8,-4.4))
        assert stroke.payload['classification_context_source']=='detector_bracket_geometry'
        geometry=stroke.payload['participant_geometry_context']
        assert geometry['status']=='estimated'
        assert list(geometry['estimate']['source_frames'])==[7,9]
    else:
        assert context.hitter_court_xy is None
        assert stroke.payload.get('classification_context_source')!='named_player'

def test_capability_exposes_missing_named_binding_and_review_action(tmp_path):
    engine,_,_,_=setup(tmp_path)
    disabled=ModelChoice(model='none',backend='none')
    profile=Profile(name='identity-boundary',shuttle=disabled,player_detector=disabled,pose=disabled,stroke=disabled,contact=disabled)
    session=BadmintonSession.__new__(BadmintonSession)
    session.engine=engine
    session.session=Session(session_id='S1',title='India identity configuration',source=Source(kind=SourceKind.UPLOAD,uri='controlled-fixture.mp4'),media=MediaInfo(fps_num=30,fps_den=1,n_frames=17,width=1280,height=720,duration_us=566667),players=[PlayerInfo(player_id=key,name=value)for key,value in NAMES.items()],roster=ParticipantRoster(match_format='singles'))
    session.perception=SimpleNamespace(profile=profile,models={},degraded=[],runtimes={},scoreboard=None,match_format='singles')
    capability=session.capabilities().get('named_identity')
    assert capability is not None
    assert capability['status']=='review_required'
    assert 'bind' in capability['reason'].lower()
    assert capability['review_action']

def test_existing_scoped_review_can_credit_loh_without_rewriting_machine_identity(tmp_path):
    engine,store,capture,item=setup(tmp_path)
    stroke,_=classify(engine,store,capture,item)
    hypothesis=stroke.payload.get('participant_hypothesis')
    assert isinstance(hypothesis,dict)and hypothesis['status']=='provisional'
    assert stroke.actors.player_id is None
    official_fixture(store,stroke)
    ledger=IdentityReviewLedger(store,{'sen','loh'},max_frame=16,fps=30)
    birth=store.get(hypothesis['observation_id']);assert birth is not None
    review=ledger.confirm(birth.event_id,'loh',birth.frame_start,16)
    # The existing API requires the reviewer to confirm this stroke separately.
    assert review.payload['applied_to_attribution']is False
    before=build_individual_analytics(store,roster(),max_frame=16,fps=30)
    assert before['accounting']['attributed_shots']==0
    scoped=ledger.confirm_stroke(stroke.event_id,review.event_id)
    assert scoped.actors.player_id=='loh'
    after=build_individual_analytics(store,roster(),max_frame=16,fps=30)
    assert after['participants']['loh']['total_shots']==1
    assert after['participants']['sen']['total_shots']==0
    assert store.get(stroke.event_id).actors.player_id is None
    assert item.event.actors.player_id is None
