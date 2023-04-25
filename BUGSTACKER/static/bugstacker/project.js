// Execute after content has been loaded
import { setAllDisplayProps, returnProjectBodyObject, manageProjectChangeUI } from './helpers.js';

document.addEventListener('DOMContentLoaded', function () {

  // Boostrap Modal
  // const myModal = document.getElementById('myModal')
  // const myInput = document.getElementById('myInput')
  //   myModal.addEventListener('shown.bs.modal', () => {
  //   myInput.focus()
  // })

  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
  const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))


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


  // API Requests

  // Apply Event Handlers for manageProject()
  const changeProjectStatusBtn = document.getElementById('changeProjectStatusBtn');
  const completeProjectBtn = document.getElementById('completeProjectBtn')

  changeProjectStatusBtn.onclick = manageProject;
  completeProjectBtn.onclick = manageProject;

  // Apply Event Handlers for manageWorkflow()
  const manageWorkflowBtns = document.querySelectorAll('.manageWorkflowBtn');
  for (let i = 0; i < manageWorkflowBtns.length; i++) {
    manageWorkflowBtns[i].onclick = manageWorkflow;
  }
  console.log(manageWorkflowBtns);

  // Apply Event Handlers for manageTicket()
  const manageTicketBtns = document.querySelectorAll('.manageTicketBtn');
  for (let i = 0; i < manageTicketBtns.length; i++) {
    manageTicketBtns[i].onclick = manageTicket;
  }
  console.log(manageTicketBtns);


  // Manage Project
  function manageProject(event) {
    event.preventDefault();

    // Get URL arguments
    const action = event.target.dataset.action;
    const target = event.target.dataset.target;

    console.log(action);
    console.log(target);

    // Assign Body object
    let bodyObj = returnProjectBodyObject(action, event.target)

    // Request Resource change
    fetch(`/project/${action}/${target}`, {
      method: 'PATCH',
      body: JSON.stringify(bodyObj)
    })
    .then(response => response.json())
    .then(data => {
      if (!data.error) {
        console.log(data.message)
        manageProjectChangeUI(action, event.target)
      } else {
        console.error(data.error)
      }
    })
    .catch(error => {
      console.error(error)
    })
  }


  // Manage workflow
  function manageWorkflow(event) {
    event.preventDefault();

    // Get URL arguments
    const action = event.target.dataset.action;
    const project = event.target.dataset.project;
    const target = event.target.dataset.target;

    console.log(action);
    console.log(project);
    console.log(target);

    // Check action and target values

    // Request Resource change
    fetch(`/workflow/${action}/${project}/${target}`, {
      method: 'PATCH',
      body: JSON.stringify({
        action: action,
        project: project,
        target: target,
      })
    })
      .then(response => response.json())
      .then(data => {
        if (!data.error) {
          console.log(data.message)
        } else {
          console.error(data.error)
        }
      })
      .catch(error => {
        console.error(error)
      })
  }


  // Manage ticket
  function manageTicket(event) {
    event.preventDefault();

    // Get URL arguments
    const action = event.target.dataset.action;
    const project = event.target.dataset.project;
    const workflow = event.target.dataset.workflow;
    const target = event.target.dataset.target;

    console.log(action);
    console.log(project);
    console.log(workflow);
    console.log(target)

    // Check action and target values

    // Request Resource change
    fetch(`/ticket/${action}/${project}/${workflow}/${target}`, {
      method: 'PATCH',
      body: JSON.stringify({
        action: action,
        project: project,
        workflow: workflow,
        target: target,
      })
    })
    .then(response => response.json())
    .then(data => {
      if (!data.error) {
        console.log(data.message)
      } else {
        console.error(data.error)
      }
    })
    .catch(error => {
      console.error(error)
    })
  }

})



