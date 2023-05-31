export function setAllDisplayProps(element, display) {

  const displays = [
    'inline',
    'block',
    'flex',
    'grid',
    'inline-block',
    'inline-flex',
    'inline-grid',
    'none',
  ]

  // Check arguments
  if (!(element instanceof HTMLElement) & !(element instanceof SVGElement)) {
    throw new Error('Element(s) must be an instance of an "HTMLElement" or "SVGElement.');
  }

  if (typeof display !== 'string') {
    throw new Error('display property must be a string.');
  }

  if (!displays.includes(display)) {
    throw new Error(`display type "${display}" not allowed.`);
  }

  // Set target element display
  element.style.display = display;

  const children = element.children;

  for (let i = 0; i < children.length; i++) {
    setAllDisplayProps(children[i], display)
  }
}


export function returnProjectBodyObject(action, target) {

  if (action === "change_status") {
    if (target.dataset["status"]) {
      return {'current_status': target.dataset["status"]}
    } else {
      throw new Error('No data-status attribute defined.')
    }
  } else if (action === "complete") {
    return {}
  } else {
    throw new Error('data-action attribute has unusable value.')
  }
}


export function manageProjectChangeUI(action, eventTarget) {

  if (action === 'change_status') {
    let element = document.querySelector('#projectName')
    if (eventTarget.dataset['status'] === 'A') {


      // Show Reactivate Btn, show Inactive status change current status to Inactive
      eventTarget.setAttribute('data-status', 'I');
      eventTarget.innerHTML = 'Reactivate';
      document.querySelector('#projectStatus').innerHTML = 'Inactive';
      element.style = "color: red!important";
      console.log("Deactivate button should be Reactivate now");

    } else if (eventTarget.dataset['status'] === 'I') {

      // Show Deactivate Btn, show Active status and change current status to Active
      eventTarget.setAttribute('data-status', 'A');
      eventTarget.innerHTML = 'Deactivate';
      document.querySelector('#projectStatus').innerHTML = 'Active';
      element.style = "color: white!important";
      console.log("Reactivate button should be Deactivate now");
    }
  }

  if (action === 'complete') {
    const pageDiv = document.querySelector('.main-content');
    const pageBtns = pageDiv.querySelectorAll('button');
    pageBtns.forEach((element) => element.disabled = 'true')
    console.log("buttons should be disabled");
  }

}


export function populateEditWorkflowInputs(target_wf_hrc) {

  // Convert hrc to mrc
  const target_wf_mrc = target_wf_hrc.slice(1)

  // Get form inputs
  const nameInput = document.getElementById('editWorkflowFormNameInput');
  const descriptionInput = document.getElementById('editWorkflowFormDescriptionInput');

  // Get selected workflow data
  const wfName = document.querySelector(`h5[data-wf="${target_wf_mrc}"]`).dataset.name;
  const wfDescription = document.querySelector(`p#wfdesc_${target_wf_mrc}`).innerHTML;

  // Update form inputs to reflect the selected workflow
  nameInput.value = wfName;
  descriptionInput.value = wfDescription;
}


export function populateEditTicketInputs(target_ticket_hrc) {

  // Convert hrc to mrc
  const target_ticket_mrc = target_ticket_hrc.split("-")[2].slice(1)
  const target_wf_mrc = target_ticket_hrc.split("-")[1].slice(1)

  
}