/**Code from: https://materializecss.com/navbar.html */
/** Side navigation*/
$(document).ready(function(){
    $('.sidenav').sidenav({edge: 'right'});
  });

/** Tool Tip */
  $(document).ready(function(){
    $('.tooltipped').tooltip();
  });

/** Datepicker & Categories Dropdown */
$(document).ready(function(){
  $('select').formSelect();
  $('.datepicker').datepicker({
    format: "dd,mmmm,yyyy",
    yearRange: 3,
    showClearBtn: true,
    i18n: {
      done: "Select"
    }
  });
});
