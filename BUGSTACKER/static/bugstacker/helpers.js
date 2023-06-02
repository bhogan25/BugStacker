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

  // Set target display
  element.style.display = display;

  // Recursively call self on all target element's children
  const children = element.children;

  for (let i = 0; i < children.length; i++) {
    setAllDisplayProps(children[i], display)
  }
}


export function manageProjectChangeUI(action, eventTarget) {

  if (action === 'change_status') {
    const projectTitleElement = document.querySelector('#projectName')
    const completeBtn = document.querySelector('#initiateComplete')

    if (eventTarget.dataset['status'] === 'A') {

      // Show Reactivate Btn, show Inactive status change current status to Inactive
      eventTarget.setAttribute('data-status', 'I');
      eventTarget.innerHTML = 'Reactivate';
      document.querySelector('#projectStatus').innerHTML = 'Inactive';
      projectTitleElement.style = "color: #AC0000!important";

      // Activate Complete Button
      completeBtn.disabled = false;

    } else if (eventTarget.dataset['status'] === 'I') {

      // Show Deactivate Btn, show Active status and change current status to Active
      eventTarget.setAttribute('data-status', 'A');
      eventTarget.innerHTML = 'Deactivate';
      document.querySelector('#projectStatus').innerHTML = 'Active';
      projectTitleElement.style = "color: #E4E8EC!important";

      // Deactivate Complete Button
      completeBtn.disabled = true;
    }
  }

  if (action === 'complete') {
    const pageDiv = document.querySelector('.main-content');
    const pageBtns = pageDiv.querySelectorAll('button');
    pageBtns.forEach((element) => element.disabled = 'true')
  }

}


export function populateEditWorkflowInputs(target_wf_hrc) {

  if (target_wf_hrc !== "") {
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
}


// Triger boostrap alert
export const appendAlert = (message, type) => {
  const alertPlaceholder = document.getElementById('liveAlertPlaceholder');
  const wrapper = document.createElement('div');
  wrapper.innerHTML = [
    `<div class="alert alert-${type} alert-dismissible" role="alert">`,
    `   <div>${message}</div>`,
    '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
    '</div>'
  ].join('')

  alertPlaceholder.append(wrapper);
}