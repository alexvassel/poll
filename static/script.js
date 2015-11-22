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

        var ERROR = 'Ни один из вариантов не выбран';

        if (select.val() === null)
        {
            alert(ERROR);
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
          success: function(){
            $(select).prop('disabled', 'disabled');
            currentButton.hide();
          },
        });
    });
});
