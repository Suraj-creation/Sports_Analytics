// Hand-authored illustration data. These are not measured match events.
const phases = [
  { title: 'Preparation', image: './assets/preparation.webp', alt: 'Generated preparation scene of a badminton player', question: 'preparation',
    points: [[1177,287],[1141,326],[1243,332],[1030,372],[898,394],[1311,302],[1308,249],[1154,458],[1218,468],[1180,598],[1256,584],[1246,739],[1288,663]],
    chains: [[0,1,2],[1,3,4],[2,5,6],[1,7,8,2],[7,9,11],[8,10,12]], marker: [136,244], trail: 'M1270 865 Q1170 845 1150 815' },
  { title: 'Contact candidate', image: './assets/contact.webp', alt: 'Generated overhead striking scene with the racket extended', question: 'contact',
    points: [[1169,291],[1114,337],[1211,327],[1044,419],[963,452],[1211,238],[1189,137],[1154,467],[1211,480],[1192,604],[1252,589],[1244,731],[1290,667]],
    chains: [[0,1,2],[1,3,4],[2,5,6],[1,7,8,2],[7,9,11],[8,10,12]], marker: [115,209], trail: 'M1270 865 Q1160 840 1155 809' },
  { title: 'Recovery', image: './assets/recovery.webp', alt: 'Generated recovery scene with the player back in a ready stance', question: 'recovery',
    points: [[1198,359],[1151,400],[1227,401],[1101,468],[1044,535],[1232,476],[1207,546],[1145,550],[1220,550],[1074,670],[1264,675],[1103,802],[1305,777]],
    chains: [[0,1,2],[1,3,4],[2,5,6],[1,7,8,2],[7,9,11],[8,10,12]], marker: [103,228], trail: 'M1300 840 Q1200 872 1110 815' },
];
const answers = {
  preparation: { status: 'Illustrated observation', title: 'The shot starts before contact.', body: 'Preparation gives the overhead action its context. In the product, related event frames let you look at what happened before a selected moment.', phase: 0, citation: 'View the preparation scene' },
  recovery: { status: 'Illustrated observation', title: 'The recovery belongs to the story.', body: 'The player returns to a ready position after the overhead action. Following the sequence makes the moment easier to understand.', phase: 2, citation: 'View the recovery scene' },
  contact: { status: 'Candidate event', title: 'A useful moment to investigate.', body: 'This scene illustrates a possible contact window. A real contact claim needs temporal evidence; a pose or a single frame does not confirm the exact instant.', phase: 1, citation: 'Inspect the contact candidate' },
  speed: { status: 'Insufficient evidence', title: 'We cannot measure that here.', body: 'These generated scenes cannot establish shuttle speed. A reliable measurement needs appropriate trajectory evidence, timing and calibration. No speed value is supplied.', phase: null, citation: '' },
};
export function getPhase(index) {
  if (!Number.isInteger(index) || index < 0 || index >= phases.length) throw new RangeError('Unknown illustration phase');
  return phases[index];
}
export function getAnswer(id) {
  if (!Object.hasOwn(answers, id)) throw new RangeError('Unknown example question');
  return answers[id];
}
export const phaseCount = phases.length;
