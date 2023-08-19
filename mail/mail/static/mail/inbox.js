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
        console.log(result);
        load_mailbox('sent'); // Load the user's sent mailbox
    });
  });
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Clear previous emails
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    emails.forEach(email => {
      const emailDiv = document.createElement('div');
      emailDiv.style.border = '1px solid gray';
      emailDiv.style.borderRadius = '0.25rem';
      emailDiv.style.padding = '10px';
      emailDiv.style.margin = '5px';
      emailDiv.style.background = email.read ? 'lightgray' : 'white';
      emailDiv.style.cursor = 'pointer';


      emailDiv.innerHTML = `
        <strong>From:</strong> ${email.sender}<br>
        <strong>Subject:</strong> ${email.subject}<br>
        <strong>Timestamp:</strong> ${email.timestamp}
      `;

      emailDiv.addEventListener('click', () => {
        fetch(`/emails/${email.id}`)
        .then(response => response.json())
        .then(email => {
          const emailView = document.createElement('div');
          emailView.innerHTML = `
            <h3>${email.subject}</h3>
            <p><strong>From:</strong> ${email.sender}</p>
            <p><strong>To:</strong> ${email.recipients.join(', ')}</p>
            <p><strong>Timestamp:</strong> ${email.timestamp}</p>
            <p>${email.body}</p>
          `;

          // Reply button
          const replyButton = document.createElement('button');
          replyButton.textContent = 'Reply';
          replyButton.addEventListener('click', () => {
            compose_email();
            document.querySelector('#compose-recipients').value = email.sender;
            document.querySelector('#compose-subject').value = email.subject.startsWith('Re: ') ? email.subject : `Re: ${email.subject}`;
            document.querySelector('#compose-body').value = ``;
          });
          emailView.appendChild(replyButton);

          // Archive/Unarchive button
          if (mailbox !== 'sent') {
            const archiveButton = document.createElement('button');
            archiveButton.textContent = email.archived ? 'Unarchive' : 'Archive';
            archiveButton.addEventListener('click', () => {
              fetch(`/emails/${email.id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    archived: !email.archived
                })
              })
              .then(() => load_mailbox('inbox'));
            });
            emailView.appendChild(archiveButton);
          }

          document.querySelector('#emails-view').innerHTML = '';
          document.querySelector('#emails-view').appendChild(emailView);

          // Mark the email as read
          fetch(`/emails/${email.id}`, {
            method: 'PUT',
            body: JSON.stringify({
                read: true
            })
          });
        });
      });

      document.querySelector('#emails-view').appendChild(emailDiv);
    });
  });
}
