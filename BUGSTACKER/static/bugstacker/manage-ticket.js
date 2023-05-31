
// Triger boostrap alert
const appendAlert = (message, type) => {
    const alertPlaceholder = document.getElementById('liveAlertPlaceholder')
    const wrapper = document.createElement('div')
    wrapper.innerHTML = [
      `<div class="alert alert-${type} alert-dismissible" role="alert">`,
      `   <div>${message}</div>`,
      '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
      '</div>'
    ].join('')

    alertPlaceholder.append(wrapper)
}


// For Card Tickets
class ChangeTicketStatusBtn extends React.Component {
    constructor(props) {
        super(props)
    }

    render() {
        let text;
        function displayInnerText(status) {
            switch (status) {
                case "C":
                  text = "Start";
                  break;
                case "IP":
                  text = "Resolve";
                  break;
                case "D":
                  text = "Ticket is Done";
                  break;
              }
              return text;
        }
        return (
            <button onClick={this.props.handleClick} 
                    type="button" 
                    className="btn btn-success me-4 tool" 
                    style={{display: this.props.propDipslay}} 
                    title={this.props.propsTitle} 
                    disabled={this.props.ticketStatus === "D" ? true : false} 
                    data-ticket-hrc={this.props.ticketHrc} 
                    data-bs-toggle={this.props.ticketStatus === "IP" ? "modal" : ""} 
                    data-bs-target={this.props.ticketStatus === "IP" ? "#ticketResolutionModal" : ""}>
                {displayInnerText(this.props.ticketStatus)}
            </button>
        )
    }
}


class ManageTicketBtnGroup extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            ticketStatus: this.props.ticketStatus,
            ticketResolution: this.props.ticketResolution,
            ticketChildButtonsShown: false,
        }
        this.sendNewStatus = this.sendNewStatus.bind(this);
        this.startTicket = this.startTicket.bind(this);
        this.resolveTicket = this.resolveTicket.bind(this);
        this.setHandleClick = this.setHandleClick.bind(this);
        this.toggleChildBtns = this.toggleChildBtns.bind(this);
        this.populateEditTicketModal = this.populateEditTicketModal.bind(this);
    }


    startTicket() {
        this.sendNewStatus("IP");
    }

    resolveTicket() {

        // Redefine sendNewStatus() so anon functions can access
        const send = this.sendNewStatus;

        // Get Modal Header and Submit button
        const ticketModalLabel = document.getElementById("ticketResolutionModalLabel");
        const submitBtn = document.getElementById("resolutionModalSubmitBtn");

        // Add Title Header
        ticketModalLabel.innerHTML = this.props.ticketName;

        // Determine if radio is selected
        const radioSelection = function () {

            // Get DOM resolution option elements
            const options = document.getElementsByName("resolution");

            for (let i = 0; i < options.length; i++) {
                if (options[i].checked) {
                    return options[i].value;
                }
            }
            return null;
        }

        // Event listener on radio select options to toggle submit btn
        const options = document.getElementsByName("resolution");

        const toggleSubmitBtn = function () {
            if (radioSelection()) {
                submitBtn.disabled = false;
            } else {
                submitBtn.disabled = true;
            }
        }

        for (let i = 0; i < options.length; i++) {
            options[i].addEventListener("change", toggleSubmitBtn)
        }

        // fetch request event to trigger
        const submitResolution = function () {
            let selectedOption = radioSelection();

            if (selectedOption) {
                send("D", selectedOption)
            }

            // Remove event listener on click
            submitBtn.removeEventListener("click", submitResolution)
        }

        // Submit event listener
        submitBtn.addEventListener("click", submitResolution)
    }

    // Fetch Request for Ticket Status
    sendNewStatus(newStatus, resolution = null) {

        // Get Project, Workflow Code
        const projectCode = window.location.href.split('/').pop();
        const workflowCode = this.props.ticketHrc.split('-')[0].slice(1);               // FIX: Change to harvest from ticket_hcr
        const ticketCode = this.props.ticketHrc.split('-')[1].slice(1);                 // FIX: Change to harvest from ticket_hcr

        // Get Status div for Card and Table Row Ticket
        const ticketStatusElements = document.querySelectorAll(`#${this.props.ticketHrc} [data-ticket-status]`)

        // Define Status Transform Object
        const STO = {
            "C": "Created",
            "IP": "In Progress",
            "D": "Done",
        };

        // Send Fetch Request to advance status
        fetch(`/ticket/advance-status/${projectCode}/${workflowCode}/${ticketCode}`, {
            method: 'PUT',
            body: JSON.stringify({
                ticketStatus: newStatus,
                resolution: resolution,
            })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.error) {
                // Success, update UI, alert
                this.setState({
                    ...this.state,
                    ticketStatus: newStatus,
                });
                console.log(data.message)
                // Update ticket status for Card
                ticketStatusElements.forEach((element) => element.innerHTML = `${STO[newStatus]}`)

                // Update ticket status for Card

                appendAlert(`Ticket ${this.props.ticketHrc} has been set to ${STO[newStatus]}`, 'success')
            } else {
                // Server Error, do not update UI, alert
                console.error(`${data.error}`)
                appendAlert(`Error advancing ticket ${this.props.ticketHrc} status to ${STO[newStatus]} was unsuccessful`, 'danger')
            }
        })
        .catch(error => {
            // Client Error, do not update UI, alert
            console.error(`Client Error during advancing ticket status to ${STO[newStatus]} state \n ${error}`)
            appendAlert(`Request to advance ticket status to ${ticketCode} was unsuccessful`, 'warning')
        })
    }

    // Set handle click for advance status button
    setHandleClick() {
        let handleClickFn;
        switch (this.state.ticketStatus) {
            case "C":
              handleClickFn = this.startTicket;
              break;
            case "IP":
              handleClickFn = this.resolveTicket;
              break;
            case "D":
              handleClickFn = null;
              break;
          }
          return handleClickFn;
    }

    // Toggle display settings for child buttons
    toggleChildBtns() {
        if (this.state.ticketChildButtonsShown === false) {
            this.setState({
                ...this.state,
                ticketChildButtonsShown: true,
            });
        } else {
            this.setState({
                ...this.state,
                ticketChildButtonsShown: false,
            });
        }
    }

    populateEditTicketModal() {

        // Get Edit Ticket Modal Inputs
        const modalTitle = document.querySelector("#editTicketFormModalLabel")
        const textareaDescription = document.querySelector("#editTicketFormModal textarea[name='description']");
        const selectAssignees = document.querySelector("#editTicketFormModal select[name='assignees']");

        // Get Ticket Assingees, Description, and Title
        const ticketName = document.querySelector(`#${this.props.ticketHrc} h1[data-ticket-name]`).dataset['ticketName'];
        const currentDescription = document.querySelector(`#${this.props.ticketHrc} p[data-ticket-description]`).dataset['ticketDescription'];

        const currentAssigneesRaw = document.querySelector(`#${this.props.ticketHrc} div[data-ticket-assignees]`).dataset.ticketAssignees;
        let currentAssignees;

        if (currentAssigneesRaw.includes("-")) {
            currentAssignees = currentAssigneesRaw.split("-")
        } else {
            currentAssignees = currentAssigneesRaw;
        }

        // Clear/Reset Select Values
        const selectAssigneesArray = Array.from(selectAssignees.children)
        selectAssigneesArray.forEach((option) => option.selected = false);
        
        // Set form values to ticket data values
        modalTitle.innerHTML = `Edit Ticket: ${ticketName}`;
        textareaDescription.value = currentDescription;

        for (let i = 0; i < selectAssignees.children.length; i++) {
            if ( currentAssignees.includes( selectAssignees.children[i].innerHTML.trim().split(" (").shift() ) ) {
                selectAssignees.children[i].selected = true;
            }
        }
    }


    render() {
        const ticketHrc = this.props.ticketHrc;
        return (
            <div>
                <button onClick={this.toggleChildBtns} 
                        type="button" 
                        class="manageTicketBtn btn btn-primary me-4 tool" 
                        title={this.state.ticketChildButtonsShown === false ? "Show manage ticket buttons" : "Hide manage ticket buttons"}>
                    {this.state.ticketChildButtonsShown === false ? "Manage" : "Hide"}
                </button>

                <button type="button" 
                        className="show btn btn-dark me-4 tool" 
                        style={{display: this.state.ticketChildButtonsShown === true ? "inline-block" : "none"}} 
                        onClick={this.populateEditTicketModal}
                        title="Edit ticket"
                        data-bs-toggle="modal" 
                        data-bs-target="#editTicketFormModal">
                    Edit
                </button>
                <ChangeTicketStatusBtn 
                    handleClick={this.setHandleClick()} 
                    ticketStatus={this.state.ticketStatus} 
                    propDipslay={this.state.ticketChildButtonsShown === true ? "inline-block" : "none"} 
                    propTitle={this.state.ticketStatus === 'C' ? 'Flag this ticket as "started" (irreversible)' : 'Resolve this ticket. Once resolved, this ticket will be considered completed and will not be availible to be edited.'}
                    ticketHrc={ticketHrc} 
                />
            </div>
        )
    }
}

// Render ticket buttons for each Card
const ticketInstances = document.querySelectorAll('.manage-ticket-btns');

ticketInstances.forEach((e) => {
    if (e.dataset["status"] !== "D" | e.dataset["resolution"] === "NF") {
        ReactDOM.render(<ManageTicketBtnGroup 
                            ticketHrc={e.dataset["ticketHrc"]}                     /// FIX: Change Prop Name and harvest attribute
                            ticketName={e.dataset["name"]}
                            ticketStatus={e.dataset["status"]} 
                            ticketResolution={e.dataset["resolution"] 
         }/>, e)
    }
});