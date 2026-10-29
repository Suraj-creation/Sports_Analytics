import { investigate } from './catalogue-data.js';
import { inspectRally } from './catalogue.js';

export function setupInvestigation() {
  const form=document.querySelector('#investigation-form'), input=document.querySelector('#investigation-question');
  const steps=document.querySelector('#investigation-steps'), answer=document.querySelector('#investigation-answer');
  function run() {
    const result=investigate(input.value);
    steps.replaceChildren();
    for(const step of result.steps) {
      const item=document.createElement('li'), body=document.createElement('div'), title=document.createElement('strong'), detail=document.createElement('p');
      title.textContent=step.title;
      if(step.tool){const tool=document.createElement('code');tool.textContent=step.tool;title.append(tool);}
      detail.textContent=step.detail;body.append(title,detail);item.append(body);steps.append(item);
    }
    answer.querySelector('.answer-kind').textContent=result.supported?'Supported by the sample record':'Evidence unavailable';
    answer.querySelector('p').textContent=result.text;
    const citations=document.querySelector('#investigation-citations');citations.replaceChildren();
    for(const id of result.evidence) {
      const button=document.createElement('button');button.className='citation';button.textContent='Inspect '+id;button.addEventListener('click',()=>inspectRally(id));citations.append(button);
    }
  }
  form.querySelector('button').disabled=false;
  form.addEventListener('submit',event=>{event.preventDefault();run();});
  document.querySelectorAll('[data-ask-example]').forEach(button=>{button.disabled=false;button.addEventListener('click',()=>{input.value=button.dataset.askExample;run();});});
  run();
}
