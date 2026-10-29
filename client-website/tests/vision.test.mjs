import test from 'node:test';
import assert from 'node:assert/strict';
import { poseData } from '../src/pose-data.js';
import { visiblePose, poseThreshold } from '../src/vision.js';

test('both generated scenes have bounded 17-point estimates in their own image coordinate system',()=>{
  for(const record of Object.values(poseData)){
    assert.equal(record.keypoints.length,17);
    assert.equal(record.kind,'offline-2d-estimate-on-generated-scene');
    for(const [x,y,confidence] of record.keypoints){
      assert.ok(x>=0&&x<=record.width);
      assert.ok(y>=0&&y<=record.height);
      assert.ok(confidence>=0&&confidence<=1);
    }
  }
});
test('pose edges never display a joint omitted by the confidence threshold',()=>{
  for(const scene of Object.keys(poseData)){
    const {points,edges}=visiblePose(scene), ids=new Set(points.map(point=>point.id));
    assert.ok(points.length>0&&points.length<17);
    assert.ok(points.every(point=>point.confidence>=poseThreshold));
    assert.ok(edges.every(([a,b])=>ids.has(a)&&ids.has(b)));
  }
});
test('unrecognised scenes cannot fabricate a pose',()=>{
  assert.deepEqual(visiblePose('missing'),{points:[],edges:[]});
});
