const roles = { player: 'Player', coach: 'Coach', venue: 'Club or venue', partner: 'Platform partner' };
const sources = { fixed: 'Fixed court camera', phone: 'Phone recording', broadcast: 'Broadcast footage', unknown: 'To be discussed' };

export function buildBrief({ role, source, goal }, brandName = 'Rally') {
  if (!Object.hasOwn(roles, role)) throw new Error('Choose a valid role.');
  if (!Object.hasOwn(sources, source)) throw new Error('Choose a recording setup.');
  const cleanGoal = typeof goal === 'string' ? goal.trim() : '';
  if (cleanGoal.length < 10 || cleanGoal.length > 1200) throw new Error('Describe your goal in 10 to 1200 characters.');
  return `${brandName} demo discussion\n\nExploring as: ${roles[role]}\nRecording setup: ${sources[source]}\n\nWhat I would like to understand:\n${cleanGoal}\n\nQuestions for the conversation:\n- Is this footage suitable for the supported workflow?\n- Which observations and analytics would the evidence support?\n- What access, participant permissions and recording conditions need to be agreed?\n\nPrepared locally. This brief has not been sent.\n`;
}
