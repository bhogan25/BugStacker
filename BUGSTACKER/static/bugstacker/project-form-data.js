document.addEventListener('DOMContentLoaded', function () {

  // Get project data
  const projectName = document.getElementById('projectName').innerHTML.trim();
  const projectDescription = document.getElementById('projectDescription').innerHTML.trim();
  const teamMemberElements = document.querySelectorAll(".team-member");
  const teamMemeberNames = [];

  for (let i = 0; i < teamMemberElements.length; i++) {
    teamMemeberNames.push(teamMemberElements[i].innerHTML.trim().split(" - ").shift());
  }


  // Get project form inputs
  const inputName = document.querySelector('form#editProjectForm input[name="name"]');
  const textareaDescription = document.querySelector('form#editProjectForm textarea[name="description"]');
  const selectTeamMembers = document.querySelector('form#editProjectForm select[name="team_members"]');

  // Set form values to project data values
  inputName.value = projectName;
  textareaDescription.value = projectDescription;


  for (let i = 0; i < selectTeamMembers.children.length; i++) {
    if ( teamMemeberNames.includes( selectTeamMembers.children[i].innerHTML.trim().split(" (").shift() ) ) {
      selectTeamMembers.children[i].selected = true;
    }
  }
})

