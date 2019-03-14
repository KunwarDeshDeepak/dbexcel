wsname = document.getElementById('wsname');
onwschange = document.getElementById('onwschange');
onchangehead = document.getElementById('onchangehead')
let r;
function ssnamechange(obj) {
    wsname.innerHTML = "<option value=''></option>";
    result = temp(obj.value).then(()=>{
        console.log(result);
    });
        result = ['Sheet1'];
        for (let i = 0; i < result.length; i++) {
            wsname.innerHTML += "<option>" + result[i] + "</option>";
        }
        console.log(obj.value);
        wsname.style.display = "block";
        
        
}

function getsheets(ss) {
    var Http = new XMLHttpRequest();
    var url = 'https://9dd59391.ngrok.io/sheets/1PO_Dd9M9baSBGoW181FOV-jGZcbkBK0Pa_hYRtyaVjY/worksheets/';
    var promise1 = new Promise(function (resolve, reject) {
        Http.open("GET", url, true);
        Http.send(null);
        Http.onreadystatechange = (e) => {
            console.log(Http.responseText);
        }
        var sheets = Http.responseText;
        resolve(sheets);
    });


    // return result;
    //   promise1.then(function(value) {
    //     console.log(value);
    //     return arr;
    //     // expected output: "Success!"
    //   });


    // let promise1 = new Promise( (resolve, reject) => {

    //     let dataReceivedSuccessfully = false; 
    //     if (dataReceivedSuccessfully) 
    //       resolve('Data Available!'); 
    //     if (!dataReceivedSuccessfully) 
    //       reject('Data Corrupted!'); 
    //     }) 
    //     promise1.then( (message) => {
    //         console.log(message); 
    //         }).catch( (message) => {
    //            console.log(message);
    //      })


    // return [ss+" worksheet1", ss+" worksheet2"];
}
async function temp(ss){
    var result = await getsheets(ss);
    return result;
}

function wsnamechange(obj) {
    // var Http = new XMLHttpRequest();
    // var url = 'https://9dd59391.ngrok.io/sass/api_fields/?app=Jira&action=Create new comment';
    // Http.onreadystatechange = (e) => {
    //     console.log(Http.responseText);
    // }
    // Http.open("GET", url, true)
    // Http.send(null);
    context = obj.getAttribute('label');
    listoftextbox = obj.getAttribute('class');
    // console.log(listoftextbox);
    listoftextbox=listoftextbox.toString().split('\'').join('\"');
    // console.log(listoftextbox);
    obj = JSON.parse(listoftextbox);
    console.log(obj);
    onchangehead.style.display = "block";
    onwschange.innerHTML = "";
    if (context == "Create new issue") {
        // listoftextbox = ["timestamp", "issue.id", "issue.key", "issue.name", "Project.id", "Project.key", "Project.name", "created", "priority.name", "assignee", "updatedat", "status.name", "summary", "creator.emailAddress", "creator.displayName", "subtasks"];
        listoftextbox = obj["checkboxforissue"];
    }
    else if (context == "Create new comment") {
        listoftextbox = obj["checkboxforcomment"];
        // listoftextbox = [
        //     "timestamp",
        //     "comment.id",
        //     "comment.author.displayName",
        //     "comment.body",
        //     "comment.updateAuthor.displayName",
        //     "comment.created",
        //     "comment.updated",
        //     "issue.id",
        //     "issue.key",
        //     "issue.fields.summary",
        //     "issue.project.id",
        //     "issue.project.key",
        //     "issue.project.name",
        //     "issue.assignee",
        //     "issue.priority.name",
        //     "issue.status.name",
        // ];
    }
    else {
        listoftextbox = obj["checkboxforproject"];
        // listoftextbox = [
        //     "timestamp",
        //     "project.id",
        //     "project.key",
        //     "project.name",
        //     "projectLead.emailAddress",
        //     "projectLead.displayName",
        // ];
    }
    for (let i = 0; i < listoftextbox.length; i++) {
        onwschange.innerHTML += "<input name='fields' type='checkbox' value='"+listoftextbox[i]["sheet_column"]+"'><p>" + listoftextbox[i]["sheet_column"] + "</p>";
    }
    

}