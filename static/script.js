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
        var questionId = $(select).data('question');
        var answersIds = $(select).val();



        $.ajax({
          type: "POST",
          url: currentURL,
          data: { question_id: questionId, answers_ids: answersIds },
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
        var allAnswered = $('.question-root:disabled').length == $('.question-root').length;
        var poll = $('#poll');
        var pollPk = poll.data('pk');
        var NOT_FINISHED_MESSAGE = 'Вы ответили не на все вопросы';
        var FINISHED_MESSAGE = 'Опрос завершен';
        var ERROR_MESSAGE = 'Во время запроса произошла ошибка';
        var finishUrl = poll.data('finish_url');


        e.preventDefault();

        if (allAnswered)
        {
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
                else alert(ERROR_MESSAGE);
              },
              error: function(){
                alert(ERROR_MESSAGE);
              }
            });
        }
        else
        {
            alert(NOT_FINISHED_MESSAGE);
        }
    });
});
