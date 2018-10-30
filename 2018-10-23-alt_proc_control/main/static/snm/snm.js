/**
 * Version 28.08.2018
 */

var $$ = $$ ? $$ : {};

$$ = $.extend($$,(function () {
   function $$f() {
       this.parentClass = $$f;
   }
   $$f.prototype.urlArgs = function (a) {
       /*
       *  Выделяет в URL-адресе аргументы и возвращает их в виде объекта со свойствами.
       *  Если указан аргумент, то возвращается только его значение.
       */
        var args = {};
        var query = location.search.substring(1);
        query = decodeURIComponent(query).replace(/\+/g, ' ');
        var pairs = query.split('&');
        for(var i = 0; i < pairs.length; i++) {
            var pos = pairs[i].indexOf('=');
            if (pos === -1) continue;
            var name = pairs[i].substring(0,pos);
            args[name] = pairs[i].substring(pos+1);
        }
        return a ? args[a] : args;
   };
   $$f.prototype.tableInit = function (t,url) {
       /*
       *  Загружает настройки фильтра.
       *  Делает заголовки таблицы (th) кликабельными.
       *  При нажатии на заголовок отображает окно фильтра таблицы.
       *  *  В окно фильтра загружает первый набор значений, при прокрутке до конца загружает следующий.
       *  *  При фильрации набора значений загружает первый набор значений с учетом фильрации, при прокрутке
       *  *  до конца загружает следующий.
       *  После изменения настроек фильра - сохраняет его.
       *  Применяет фильтр к таблице.
       */

   };
   $$f.prototype.alertModal = function (msg,caption,action,link,cancel){
       /*
       *  1. Выводит модальное окно с текстом msg и кнопкой caption (если caption не задано то надпись = ОК).
       *  2. Если задан cancel=true создает вторую кнопку с надписью 'отмена', обе кнопки закрывают окно.
       *  4. Если задан action проверяют текст это или функция
       *  *  если это текст, добавляют его к кнопке в качестве url для перехода
       *  *  если это функция, добаляют ее к кнопке как обработчик.
       *  5. Если задан аргумент link, то закрытие окна приводит к переходу по ссылке link,
       *  *  если link = 'back' - происходит переход на предыдущую страницу.
       *  6. Возвращает объект modal содержащий функцию close, закрывающую модальное окно.
       */
       var o = {}
       if (typeof msg === 'object') {
           o = msg;
       } else {
           o.msg = msg;
           o.caption = caption;
           o.action = action;
           o.link = link;
           o.cancel = cancel;
       } console.log('###',o,o.msg,typeof o.msg,!!o.msg);
       if (!o.msg) {
           console.log('error alertModal - message is empty');
           return;
       }
       var modal = {removed:false};
       modal.close = function () {
           if (o.action_on_close) {o.action();}
           if (o.link) {
               if (o.link === 'back') {
                   history.back();
               } else {
                   location.replace(o.link);
               }
           } else {
               modal.removed = true;
               $(modal.div).fadeOut(300, function(){
                   $(modal.div).remove();
                   delete modal.div;
               });
           }
       };
       modal.buttons = $('<div>').attr('id','am-buttons');
       o.caption = o.caption ? o.caption : 'Ok';
       var but = $('<input>',{value:o.caption, type: 'button'});
       but.appendTo(modal.buttons);
       if (o.action) {
           if (typeof o.caption === 'string' && (typeof o.action === 'string' || typeof o.action === 'function')) {
                if (typeof o.action === 'string') {
                    $('<a>',{href:o.action,append: but}).appendTo(modal.buttons);
                }
           } else {
                console.log('error alertModal - invalid parameters',but,o.caption,o.action);
                return;
           }
       }
       if (o.cancel) {$('<input>',{value:'Отмена',type:'button'}).appendTo(modal.buttons);}
       modal.div = $('<div>',{
            id:'am-overlay'
           ,on: {
                click: modal.close
           }
           ,append: $('<div>',{
                id:'am-win'
               ,append: $('<div>',{id:'am-content',html: o.msg})
                        .add(modal.buttons)
           })
       });
       modal.div.appendTo('body');
       if (o.action) {but.on('click',o.action);}
       return modal;
   };

   $$f.prototype.fieldsInit = function (container){
       /*
       *  1.Ищет в объекте container (или если объект не указан, то в body)
       *    объекты input и получает из них значение атрибута name.
       *  2.Ищет в URL (или объекте $$) свойство с именем name и получает его значение.
       *  3.Устанавливает полученное значение объекту input.
       *  4.Ищет элементы с атрибутом data-am-msg и назначает им обработчик:
       *    вызов модального окна с сообщением data-am-msg и кнопкой "Ок"
       *    Если заданы атрибуты data-am-caption и data-am-href, то кнопка
       *    "Ок" заменяется парой кнопок data-am-caption и "Отмена". При этом
       *    кнопка data-am-caption осуществляет переход по адресу data-am-href.
       */
       if (typeof $$ === 'object') {
           container = container ? container : 'body';
           $(container).find(':input').each(function(){
               var el       = $(this);
               var name     = el.prop('name');
               var val   = get_val_attr(name,$$);

               if (!val && el.prop('type') === 'radio') {
                   $('[name='+name+']:first',container).prop('checked',true);
               }

               if (!val || !name || ($.type(val) === 'object' &&
                       $.isEmptyObject(val))) return true;
               if (el.is('select')) {
                   if (val && $('[value="'+val+'"]',el).length) {
                       el.val(val);
                   } else {
                       console.log('error fieldsInit - select ',name,el,'does not contain',val);
                       $$.alertModal('Ошибка загрузки параметров:<br> type=select name='+name+' val='+val,
                           undefined,undefined,'back');
                       return false;
                   }
               } else if (el.prop('type') === 'checkbox') {
                   el.prop('checked', val);
               } else if (el.prop('type') === 'radio') {
                   var els = $('[name='+name+'][value='+val+']');
                   if (els.length === 0) {
                       console.log('error fieldsInit - radio ',name,el,'does not contain',val);
                       $$.alertModal('Ошибка загрузки параметров:<br> type=radio name='+name+' val='+val,
                           undefined,undefined,'back');
                       return false;
                   } else {
                       els.prop('checked', true);
                   }
               }
               else if (el.prop('type') !== 'button' &&
                          el.prop('type') !== 'submit' &&
                          el.prop('type') !== 'reset') {
                   el.val(val);
               }
           });
           $('[data-am-msg]').map(function(){
                var msg = $(this).attr('data-am-msg');
                if ($(this).is('[data-am-caption]') && $(this).is('[data-am-href]')) {
                    var caption = $(this).attr('data-am-caption');
                    var href = $(this).attr('data-am-href');
                    $(this).on('click',function(){$$.alertModal(msg,caption,href);});
                } else {
                    $(this).on('click',function(){$$.alertModal(msg);});
                }
           });
       }
   };

   $$f.prototype.formSubmit = function (event) {
       /*
       *  Обработчик события submit - отправка формы.
       *  1. Ищет в источнике элементы input
       *  2. Для обязательных (с атрибутом data-req) проверяет наличие значения,
       *     если значение не найдено - подсвечивает элемент, выдает ошибку и отменяет отправку формы.
       *  3. Для не обязательных (без атрибута data-req),
       *     если значение отсутствует - делает неактивными, чтоб не отправлять пустые аргументы на сервер.
       *     Если значение задано - ищет в объекте $$.default свойство совподающее с атрибутом name элемента,
       *     сравнивает их значения и, если они совпадают, делает неактивными, чтоб не отправлять на сервер.
       *  4. Если в атрибуте method указано значение POST - то отправка формы блокируется, создается
       *     форма с одним скрытым полем params, которое содержит JSON объект с уровнями вложенности.
       *     Например форма Login с полями name="user.name" и name="user.pass" может отправить конструкцию:
       *     {"user":{"name":"admin","pass":"123"}}. В случае наличия файлов к JSON объекту также добавляется
       *     список идентификаторов файлов ранее загруженных на сервер плагином "jQuery Upload File":
       *     {"files":["22345200abe84f6090c80d43c5f6c0f6"]}
       *  5. Если в параметре event.data передан параметр url = true, то добавляет параметры в url.
       */
        var err      = false;
        var target = $(event.target);
        var method = target.attr('method');
        var post = method !== undefined && method.toUpperCase() === 'POST';
        $(event.target).find(':input').each(function(){
            var el       = $(this);
            var name     = el.prop('name');
            if (!name) return true;
            var checkbox = (el.prop('type') === 'checkbox');
            var radio    = (el.prop('type') === 'radio');
            var rads     = $('input:radio[name="'+name+'"]');
            var radchk   = rads.filter(':checked');
            var radreq   = rads.filter('[data-req]');
            var empty    = radio ? (!radchk.length || (!radchk.val())) : checkbox ? false : (!el.val());
            var req      = radio ? (radreq.length > 0)   : checkbox ? false : el.is('[data-req]');

            //req?
            if (req) {
                if (empty) {
                    el.addClass('tag-error');
                    err = true;
                }
            } else if (!post) {
                if (empty) {
                    if (!checkbox) {
                        el.attr('disabled',true);
                    }
                } else {
                    if (typeof $$.default === 'object') {
                        var defval = $$.default[name];
                        if (defval) {
                            if (radio) {
                                if (String(defval) === String(radchk.val())) {
                                    radchk.attr('disabled',true);
                                }
                            } else if (checkbox) {
                                if (el.prop('checked')) {
                                    el.attr('disabled',true);
                                }
                            } else {
                                if (String(defval) === String(el.val())) {
                                    el.attr('disabled',true);
                                }
                            }
                        }
                    }
                }
            }
        });
        if (err) {
            setError('Не заполнены обязательные поля');
        } else {
            if (!Object.keys(dump_params(target,1)).length) {
                location = event.target['baseURI'].replace(location.search,'');
                return false;
            }
            if (!post) {return true;}
            if (target.attr('data-ignore') !== undefined) return true;
            var res = dump_params(target);

            var fileNames = $('#fileuploader').data('fileNames');
            if (fileNames) {
                res.files = fileNames;
            }
            var inp = $('<input>').attr('type','hidden').attr('name', '_form');
            inp.val(JSON.stringify(res));

            var action = target.attr('action');
            var form = $('<form>').attr('method','POST');
            if (event.data && event.data.url && !action) {
                var path = location.pathname+'?'+$.param(res);
                form.attr('action',path);
            }
            inp.appendTo(form);
            form.appendTo('body').submit();
        }
        return false;
    };

   if ($$.error) { setError($$.error) }
   $(':input').on('input change',delTagError);

   function setError(msg) {
       $('#err').html('<p>'+msg+'</p>');
       $('#err-callout').removeClass('hidden');
   }
   function delTagError(ev) {
       var el = $(ev.target);
       el.removeClass('tag-error');
       if (el.prop('type') === 'radio') {
            $('input:radio[name="'+el.prop('name')+'"]').removeClass('tag-error');
       }
   }
   function get_val(name,params) {
       /*
       *  Ищет в params свойство, расположенное по адресу name
       *  (адрес name рассматривается как цепочка вложенных объектов разделенных точкой)
       *  и возвращает его значение.
       */
       var snames = name.split('.');
       if (snames.length === 0) { return; }
       var sname = snames[0];
       var res = false;

       for(p in params) {
            if (!params.hasOwnProperty(p)) continue;
            if (p === sname) {
                res = true;
                break;
            }
       }
       if (res) {
           if (snames.length > 1) {
               name = snames.slice(1).join('.');
               return get_val(name,params[sname])
           } else {
               return params[sname];
           }
       }
   }
   function get_val_attr(name,params) {
       /*
       *  Если свойство name присутствует в URL, то возвращается его значение,
       *  иначе возвращается значение из params
       */
       var a = $$f.prototype.urlArgs(name);
       return a || get_val(name,params);
   }
   function dump_param(obj,name,val) {
       /*
       *  Разбирает name на цепочку имен вложенных объектов, разделенных точкой
       *  Создает в obj свойства с такими именами.
       */
       if (!name) { return obj; }
       var snames = name.split('.');
       if (snames.length === 0) { return obj; }
       var sname = snames[0];

       if (snames.length > 1) {
           obj[sname] = obj[sname] || {};
           name = snames.slice(1).join('.');
           obj[sname] = dump_param(obj[sname],name,val);
       } else {
           obj[sname] = val;
       }
       return obj;
   }
   function dump_params(container,enabled){
       /*
       *  1.Ищет в объекте container (или если объект не указан, то в body)
       *    объекты input и получает из них значение атрибута name.
       *  2.Объединяет найденные объекты в один и возвращает его.
       *  3.Если задан параметр enabled, то выбираются только элементы без атрибута disabled.
       */
       var res = {};
       if (typeof $$ === 'object') {
            container = container ? container : 'body';
            $(container).find(":input").each(function(){
                var el = $(this);
                if (enabled && (!!el.prop('disabled') || (el.prop('type') === 'checkbox' && !el.prop('checked'))) ) {
                    return true;
                }
                var name = el.prop('name');
                var radchk = el.prop('type') === 'radio' && !el.prop('checked');
                if (radchk && $('[name="'+name+'"]:checked',container).length) {
                    return true;
                }
                var val = radchk ? '' : el.prop('type') === 'checkbox' ? el.prop('checked') : el.val();
                var snames = name.split('.');

                res = dump_param(res,name,val);
            });
        }
        return res;
   }
   $().ready(function() {
       $($$.menu_id).addClass('active'); // Устанавливается подсветка текущего меню
       $($$.submenu_id).addClass('active'); // Устанавливается подсветка текущего подменю
       $('select, input:checkbox, input:radio, input:text','form[data-autosubmit]').on('change',function (e) {
          /*
           *  Для формы с атрибутом data-autosubmit
           *  добавляет к элементам select обработчик
           *  выполняющий отправку формы.
           */
          $(this).closest('form').submit();
       });
   });

   return new $$f();
}()));
