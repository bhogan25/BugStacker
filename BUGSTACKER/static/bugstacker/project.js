// Execute after content has been loaded
import { setAllDisplayProps, manageProjectChangeUI, populateEditWorkflowInputs, appendAlert } from './helpers.js';

document.addEventListener('DOMContentLoaded', function () {

  // Toggle Task View Mode

  // Get card and table buttons
  const tableViewBtn = document.getElementById('tableViewBtn');
  const cardViewBtn = document.getElementById('cardViewBtn');

  // Get containers for Table and Cards
  const table = document.getElementById('ticketTable');
  const cards = document.getElementById('ticketCards');

  tableViewBtn.onclick = function(event) {
    event.preventDefault()

    // Hide table btn & hide cards
    setAllDisplayProps(tableViewBtn, 'none');
    cards.style.display = 'none';

    // Show card btn and show table
    setAllDisplayProps(cardViewBtn, 'inline');
    table.style.display = 'block';
  }

  cardViewBtn.onclick = function(event) {
    event.preventDefault()

    // Hide card btn & hide table
    setAllDisplayProps(cardViewBtn, 'none');
    table.style.display = 'none';

    // Show table btn & show cards
    setAllDisplayProps(tableViewBtn, 'inline');
    cards.style.display = 'block';
  }


  // Toggle Active/Archived Workflow lists

  // Get Active/Archive Workflow btns
  const activeWfViewBtn = document.getElementById("activeWfViewBtn");
  const archivedWfViewBtn = document.getElementById("archivedWfViewBtn");

  // Get Workflow list elements
  const activeWfList = document.getElementById("activeWfList");
  const archivedWfList = document.getElementById("archivedWfList");

  // Active mode (clicked 'active')
  activeWfViewBtn.onclick = function(event) {
    event.preventDefault()

    // Disable active btn
    event.target.style.backgroundColor = 'transparent';
    event.target.style.color = 'rgb(255, 193, 7)';
    event.target.disabled = true;

    // Enable archived btn
    archivedWfViewBtn.disabled = false;
    archivedWfViewBtn.style.backgroundColor = 'rgb(255, 193, 7)';
    archivedWfViewBtn.style.color = 'black';

    // Show active list
    activeWfList.style.display = 'block';

    // Hide archived list
    archivedWfList.style.display = 'none';
  }

  // Archived mode (clicked 'archived')
  archivedWfViewBtn.onclick = function(event) {
    event.preventDefault()

    // Disable archived btn
    event.target.style.backgroundColor = 'transparent';
    event.target.style.color = 'rgb(255, 193, 7)';
    event.target.disabled = true;

    // Enable active btn
    activeWfViewBtn.disabled = false;
    activeWfViewBtn.style.backgroundColor = 'rgb(255, 193, 7)';
    activeWfViewBtn.style.color = 'black';

    // Show archived list
    archivedWfList.style.display = 'block';

    // Hide active list
    activeWfList.style.display = 'none';
  }


  // Edit Workflow Form dynamic input population

  // Populate initial form inputs for selected workflow
  const workflowSelectInput = document.getElementById('editWorkflowFormSelectWorkflow');
  populateEditWorkflowInputs(workflowSelectInput.value);

  // Apply Event Handler to dynamically populate inputs
  workflowSelectInput.addEventListener('change', () => {
    populateEditWorkflowInputs(workflowSelectInput.value);
  })


  // API Requests

  // Apply Event Handlers for manageProject()
  const changeProjectStatusBtn = document.getElementById('changeProjectStatusBtn');
  const completeProjectBtn = document.getElementById('completeProjectBtn')

  changeProjectStatusBtn.onclick = manageProject;
  completeProjectBtn.onclick = manageProject;

  // Apply Event Handlers for archiveWorkflow()
  const archiveUnarchiveBtns = document.querySelectorAll('.archiveUnarchiveBtn');
  for (let i = 0; i < archiveUnarchiveBtns.length; i++) {
    archiveUnarchiveBtns[i].onclick = archiveWorkflow;
  }

  // Manage Project
  function manageProject(event) {
    event.preventDefault();

    // Get URL arguments
    const action = event.target.dataset.action;
    const target = event.target.dataset.target;

    // Request Resource change
    fetch(`/project/${action}/${target}`, {
      method: 'PATCH',
    })
    .then(response => response.json())
    .then(data => {
      if (!data.error) {
        console.log(data.message)
        manageProjectChangeUI(action, event.target)

        if (action === "change_status") {
          appendAlert(`Project P${target} has been ${event.target.innerHTML.trim() === 'Reactivate' ? 'deactivated' : 'reactivated'}`, 'success')
        } else if (action === "complete") {
          appendAlert(`Project P${target} has been completed`, 'success')
        }
      } else {
        console.error(data.error)
        appendAlert(`Request on Project P${target} was unable to be completed.`, 'danger')
      }
    })
    .catch(error => {
      console.error(error)
      appendAlert(`Request on Project P${target} was unsuccessfull.`, 'warning')
    })
  }


  // Archive workflow
  function archiveWorkflow(event) {
    event.preventDefault();

    // Get URL arguments
    const action = event.target.dataset.action;
    const project = event.target.dataset.project;
    const target = event.target.dataset.target;

    // Check action and target values

    // Request Resource change
    fetch(`/workflow/${action}/${project}/${target}`, {
      method: 'PATCH',
    })
      .then(response => response.json())
      .then(data => {
        if (!data.error) {
          console.log(data.message)

          let actionCompleted;

          // Toggle archive/unarchive button text
          if (event.target.innerHTML.trim() === "Archive") {
            event.target.innerHTML = "Unarchive";
            actionCompleted = "archived";
          } else if (event.target.innerHTML.trim() === "Unarchive") {
            event.target.innerHTML = "Archive";
            actionCompleted = "unarchived";
          }

          // Alert User
          appendAlert(`Workflow W${target} has been ${actionCompleted}`, 'success');
        } else {
          console.error(data.error)
          // Alert User
          appendAlert(`Cannot complete request on workflow W${target}`, 'danger');
        }
      })
      .catch(error => {
        console.error(error)
        // Alert User
        appendAlert(`Workflow W${target} was not updated. Refresh and try again.`, 'warning');
      })
  }

})