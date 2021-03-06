$( document ).ready(function() {
    var csrftoken = $.cookie('csrftoken');

    // Перед каждым ajax запросом устанавливаем нужный нам заголовок
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    });

    //Пользователь отвечает на вопрос
    $( "button.answer" ).click(function() {
        var currentURL = window.location.href;
        var select = $(this).parent().find('select');

        var SELECT_ERROR = 'Ни один из вариантов не выбран';
        var COMMON_ERROR = 'Ошибка сохранения ответа';

        if (select.val() === null)
        {
            alert(SELECT_ERROR);
            return false;
        }

        var currentButton = $(this);

        var form = $(this).parent().find('form.question');

        $.ajax({
          type: "POST",
          url: currentURL,
          data: form.serialize(),
          dataType : "json",
          success: function(response){
            if (response.status == 200)
            {
              $(select).prop('disabled', 'disabled');
              currentButton.hide();
            }
            else alert(COMMON_ERROR);
          },
          error: function(){
            alert(COMMON_ERROR);
          }
        });
    });
    // Проверяем, что на все вопросы ответили и сохраняем ответ
    $( "a.finish-poll" ).click(function(e) {
        var poll = $('#poll');
        var pollPk = poll.data('pk');
        var NOT_FINISHED_MESSAGE = 'Вы ответили не на все вопросы';
        var FINISHED_MESSAGE = 'Опрос завершен';
        var ERROR_MESSAGE = 'Во время запроса произошла ошибка';
        var finishUrl = poll.data('finish_url');


        e.preventDefault();

        $.ajax({
          type: "POST",
          url: finishUrl,
          data: { poll_pk: pollPk },
          dataType : "json",
          success: function(response){
            if (response.status == 200)
            {
              alert(FINISHED_MESSAGE);
              location.replace('/');
            }
            else if (response.status == 400) alert(NOT_FINISHED_MESSAGE);
            else alert(ERROR_MESSAGE);
          },
          error: function(){
            alert(ERROR_MESSAGE);
          }
        });
    });
});
