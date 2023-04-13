

const myModal = document.getElementById('myModal')
const myInput = document.getElementById('myInput')

myModal.addEventListener('shown.bs.modal', () => {
  myInput.focus()
})

// function ProjectBoard() {
//   return (
//       <div>
//           Hello!
//       </div>
//   );
// }

// ReactDOM.render(< />, document.querySelector("#"));