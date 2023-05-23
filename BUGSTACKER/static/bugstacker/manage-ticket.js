
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
                    id={"changeStatusBtn_" + this.props.id} 
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
                    console.log(`Selected option is ${options[i].value}`);
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
            console.log("Submit toggler Placed")
        }

        // fetch request event to trigger
        const submitResolution = function () {
            let selectedOption = radioSelection();
            console.log("submitResolution() triggered")

            if (selectedOption) {
                console.log("selectedOption detected")
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
        const workflowCode = this.props.ticketWf;
        const ticketCode = this.props.ticketId.split("_").pop();

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
                appendAlert(`Ticket ${this.props.ticketId.split("_").pop()} has been set to ${newStatus}`, 'success')
            } else {
                // Server Error, do not update UI, alert
                console.error(`${data.error}`)
                appendAlert(`Error advancing ticket ${this.props.ticketId.split("_").pop()} status to ${newStatus} was unsuccessful`, 'danger')
            }
        })
        .catch(error => {
            // Client Error, do not update UI, alert
            console.error(`Client Error during advancing ticket status to ${newStatus} state \n ${error}`)
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


    render() {
        const ticketId = this.props.ticketId.split("_").pop();
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
                        id={"editTicketBtn_" + ticketId} 
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
                    id={ticketId} 
                />
            </div>
        )
    }
}

// Render ticket buttons for each Card
const ticketInstances = document.querySelectorAll('.manage-ticket-btns');

// Log divs to render ticket buttons inside
// for (let i = 0; i < ticketInstances.length; i++) {
//     console.log(ticketInstances[i].id);
// }

ticketInstances.forEach((e) => {
    if (e.dataset["status"] !== "D" | e.dataset["resolution"] === "NF") {
        ReactDOM.render(<ManageTicketBtnGroup 
                            ticketId={e.id} 
                            ticketName={e.dataset["name"]}
                            ticketWf={e.dataset["wf"]}
                            ticketStatus={e.dataset["status"]} 
                            ticketResolution={e.dataset["resolution"] 
         }/>, e)
    }
});