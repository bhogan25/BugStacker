// Execute after content has been loaded
document.addEventListener('DOMContentLoaded', function () {
  
  // Boostrap Modal
  // const myModal = document.getElementById('myModal')
  // const myInput = document.getElementById('myInput')
  //   myModal.addEventListener('shown.bs.modal', () => {
  //   myInput.focus()
  // })

  const tableViewBtn = document.getElementById('tableViewBtn');
  const cardViewBtn = document.getElementById('cardViewBtn');

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



function setAllDisplayProps(element, display) {

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
    throw new Error('Element must be an instance of an "HTMLElement" or "SVGElement.');
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
