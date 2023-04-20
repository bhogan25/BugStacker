// Execute after content has been loaded
import { setAllDisplayProps } from './helpers.js';

document.addEventListener('DOMContentLoaded', function () {

  // Boostrap Modal
  // const myModal = document.getElementById('myModal')
  // const myInput = document.getElementById('myInput')
  //   myModal.addEventListener('shown.bs.modal', () => {
  //   myInput.focus()
  // })


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
    // tableViewBtn.style.display = 'none';
    setAllDisplayProps(tableViewBtn, 'none');
    cards.style.display = 'none';

    // Show card btn and show table
    // cardViewBtn.style.display = 'block';
    setAllDisplayProps(cardViewBtn, 'inline');
    table.style.display = 'block';
  }

  cardViewBtn.onclick = function(event) {
    event.preventDefault()

    // Hide card btn & hide table
    // cardViewBtn.style.display = 'none';
    setAllDisplayProps(cardViewBtn, 'none');
    table.style.display = 'none';

    // Show table btn & show cards
    // tableViewBtn.style.display = 'block';
    setAllDisplayProps(tableViewBtn, 'inline');
    cards.style.display = 'block';
  }
})