async function startChallenge() {
    const phone = document.getElementById('user_phone').value;
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;

    const data = { phone_number: phone, start_date: startDate, end_date: endDate };

    const response = await fetch('/create-challenge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });

    const result = await response.json();
    alert(result.message);
}

async function discontinueChallenge() {
    const phone = document.getElementById('user_phone').value;
    const hour = document.getElementById('time').value
    const data = { phone_number: phone , time:time };

    const response = await fetch('/discontinue-challenge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });

    const result = await response.json();
    alert(result.message);
}