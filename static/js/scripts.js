// Use this file to add JavaScript to your project
function checkform() {
    var f = document.forms["registerForm"].elements;
    var cansubmit = true;
    for (var i = 0; i < f.length; i++) {
        if (f[i].value.length == 0)
            cansubmit = false;
    }
    document.getElementById('submitButton').disabled = cansubmit;
}
window.onload = checkform;


function showPass(id) {
  var x = document.getElementById("password-field-" + id);
  var y = document.getElementById("eye-toggle-" + id)
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
  y.classList.toggle("bi-eye")
} 

function filter_me() {
  const input = document.getElementById('search_term').value.toLowerCase();
  const cardContainer = document.getElementById('card-list');
  const cards = cardContainer.getElementsByClassName('card');
  for(let i = 0; i < cards.length; i++) {
      let title = cards[i].querySelector("h4.card-title");
      console.log(title);
      if(title.innerText.toLowerCase().indexOf(input) > -1) {
          cards[i].style.display = "";
      } else {
          cards[i].style.display = "none";
      }
  }
}

function password_generator( len ) {
  var length = (len)?(len):(20);
  var string = "abcdefghijklmnopqrstuvwxyz"; //to upper 
  var numeric = '0123456789';
  var punctuation = '!@#$%^&*()_+~`|}{[]\:;?><,./-=';
  var password = "";
  var character = "";
  var crunch = true;
  while( password.length<length ) {
      entity1 = Math.ceil(string.length * Math.random()*Math.random());
      entity2 = Math.ceil(numeric.length * Math.random()*Math.random());
      entity3 = Math.ceil(punctuation.length * Math.random()*Math.random());
      hold = string.charAt( entity1 );
      hold = (password.length%2==0)?(hold.toUpperCase()):(hold);
      character += hold;
      character += numeric.charAt( entity2 );
      character += punctuation.charAt( entity3 );
      password = character;
  }
  password=password.split('').sort(function(){return 0.5-Math.random()}).join('');
  console.log(password.substr(0,len));
  var new_password = password.substr(0,len);
  var passField = document.getElementById("password-field")
  passField.setAttribute('value', new_password)
  return new_password;
}