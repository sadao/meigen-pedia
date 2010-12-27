$(document).ready(function(){
    var currentDate = new Date();
    $('.newmarkList').each(function(){
        var pass       // passage time
             = 72;
        var content    // display content
             = '<img class="newmark" src="/images/newmark.jpg" alt="3日以内の新着発言" width="30" height="15" title="3日以内の新着発言"/>';
        var newmarkAttr = $(this).attr('title');
        newmarkAttr = newmarkAttr.replace(/年|月|日|時|分/g,':');
        newmarkAttr = newmarkAttr.replace(/\s|秒.*/g,'');
        var time = newmarkAttr.split(":");
        var entryDate = new Date(time[0], time[1]-1, time[2], time[3], time[4], time[5]);
        var now = (currentDate.getTime() - entryDate.getTime())/(60*60*1000); 
        now = Math.ceil(now);
        if(now <= pass){
            $(this).after(content);
        }
    });
});