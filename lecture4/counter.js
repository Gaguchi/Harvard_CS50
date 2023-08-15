let counter = 0;

function count(){
    counter++;
    document.querySelector('h1').innerHTML = counter;

    if (counter % 10 === 0){
        alert(`Count is now ${counter}`);
    }
}

document.addEventListener('DOMContentLoaded', function(){
    setInterval(count, 1000);
    document.querySelector('button').onclick = count;
})