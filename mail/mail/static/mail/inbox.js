document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  document.querySelector('#send-email').addEventListener('click', () => {
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
          recipients: document.querySelector('#compose-recipients').value,
          subject: document.querySelector('#compose-subject').value,
          body: document.querySelector('#compose-body').value
      })
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log(result);
    });
  });
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Clear previous emails
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Create a table to display emails
  const table = document.createElement('table');
  table.style.width = '100%';
  table.setAttribute('border', '1');
  const tbody = document.createElement('tbody');
  table.appendChild(tbody);

  // Create table headers
  const headerRow = document.createElement('tr');
  ['Sender', 'Subject', 'Timestamp'].forEach(headerText => {
    const th = document.createElement('th');
    th.appendChild(document.createTextNode(headerText));
    headerRow.appendChild(th);
  });
  tbody.appendChild(headerRow);

  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
      // Print emails
      console.log(emails);

      // Populate table with emails
      emails.forEach(email => {
        const row = document.createElement('tr');
        row.style.cursor = 'pointer';

        // Sender
        const senderCell = document.createElement('td');
        senderCell.appendChild(document.createTextNode(email.sender));
        row.appendChild(senderCell);

        // Subject
        const subjectCell = document.createElement('td');
        subjectCell.appendChild(document.createTextNode(email.subject));
        row.appendChild(subjectCell);

        // Timestamp
        const timestampCell = document.createElement('td');
        timestampCell.appendChild(document.createTextNode(email.timestamp));
        row.appendChild(timestampCell);

        // Click event to open email
        row.addEventListener('click', () => {
          // Code to open the email goes here
        });

        tbody.appendChild(row);
      });

      document.querySelector('#emails-view').appendChild(table);
  });

  console.log(mailbox);
}
