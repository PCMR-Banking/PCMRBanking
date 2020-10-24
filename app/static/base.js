var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

// var bankid = numeral(document.getElementById("bank_account").value);
// var formattedID = bankid.format('0000.00.00000');
// console.log(formattedID)

function enableTxt() {
  document.getElementById('changeFirstName').removeAttribute("readonly");
  document.getElementById('changeFirstName').classList.remove("readonlyfc");
  document.getElementById('changeLastName').readOnly = false;
  document.getElementById('changeLastName').classList.remove("readonlyfc");
  document.getElementById('changeEmailAddress').readOnly = false;
  document.getElementById('changeEmailAddress').classList.remove("readonlyfc");
  document.getElementById('changeCellphone').readOnly = false;
  document.getElementById('changeCellphone').classList.remove("readonlyfc");
  document.getElementById('MHsinKnapp2').removeAttribute("hidden");
  document.getElementById('resetbtn').removeAttribute("hidden");
}

function disableTxt() {
  document.getElementById('changeFirstName').readOnly = true;
  document.getElementById('changeFirstName').classList.add("readonlyfc");
  document.getElementById('changeLastName').readOnly = true;
  document.getElementById('changeLastName').classList.add("readonlyfc");
  document.getElementById('changeEmailAddress').readOnly = true;
  document.getElementById('changeEmailAddress').classList.add("readonlyfc");
  document.getElementById('changeCellphone').readOnly = true;
  document.getElementById('changeCellphone').classList.add("readonlyfc");
  document.getElementById('MHsinKnapp2').hidden = true;
  document.getElementById('resetbtn').hidden = true;
}

// document.addEventListener("click", enableTxt)

// function submit(){
//   setTimeout(function(){
//     location.reload();
//   }, 2000);
// }

// document.addEventListener("click", submit)