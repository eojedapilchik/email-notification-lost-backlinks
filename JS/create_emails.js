const test = false;
const inputConfig = input.config();
const list_of_active_templates = inputConfig.list_of_active_templates;
const template_table = base.getTable("tbltP7xF0hBCmjVyU")
const url = inputConfig.url ?? '';
const partner_url = inputConfig.partner_url ?? '';
const company = inputConfig.company ?? 'Resumedone.io';
const website = inputConfig.website ?? '';
const variables = {partner_url, url, website, company}
const email_queue_table = base.getTable("tblJaDA1FVHJIbx3b");
const record_id = inputConfig.record_id;
const contact_emails = inputConfig.contact_emails ?? '';
let [to, cc] = splitEmails(contact_emails);
if(test){
    to = "test@gmail.com"
    cc = "test@resumedone.io"
}
//console.log(to, cc);


let startDate = getStartDate();
//console.log(startDate)
if(to && record_id && partner_url && url){
    for (let i = 0; i<3 ; i++){
        const template = await template_table.selectRecordAsync(list_of_active_templates[i])
        if(i === 0 ){
            variables['end_date'] = addWorkingDays(startDate,3).toDateString();
        }
        if(template){
            const days = template.getCellValue('fldzE9XnPw1nj6PjN')
            const trigger_date = addWorkingDays(startDate, days)
            console.log(`The trigger date will be ${trigger_date.toLocaleDateString('en-GB')}`)
            const sequence = template.getCellValue('fld0Wxuxuf6YV1MgY');
            const subject = template.getCellValueAsString('fldRQECBcE38hTV32');
            const body = template.getCellValueAsString('fldVOwzhLstBS4ed7')
            const parsed_body = fillTemplate(body, variables);
            //console.log(`new body is: `, parsed_body);
            await createEmailRecord(parsed_body,subject,trigger_date, to, cc, sequence);
            startDate = trigger_date;
        }
    }
}else{
    console.error('Data is missing check required elements', to, cc, record_id, variables, partner_url, url)
}


function addWorkingDays(date, days) {
    let date_cp = new Date(date.getTime());
    let count = 0;
    while (count < days) {
        date_cp.setUTCDate(date_cp.getUTCDate() + 1);
        if (date_cp.getUTCDay() !== 0 && date_cp.getUTCDay() !== 6) {
            count++;
        }
    }
    return date_cp;
}

function getStartDate(){
    let startDate = new Date();

    // If current UTC time is after 5 PM, set startDate to tomorrow
    if (startDate.getUTCHours() >= 17) {
        startDate.setUTCDate(startDate.getUTCDate() + 1);
    }

    return startDate;
}

function fillTemplate(template, variables) {
    return template.replace(/\[(.*?)\]/g, (match, variable) => variables.hasOwnProperty(variable) ? variables[variable] : match);
}


async function createEmailRecord(body, subject, trigger_date, to, cc, sequence){

    let recordId = await email_queue_table.createRecordAsync({
        "fldrn6bb28F5B733v": trigger_date,
        "fldeoNVjJpbMNBv8d": {name: "Scheduled"},
        "fldTvm7yNZ3aniido": [{id: record_id}],
        "flduDGObmkvWscUkA": sequence,
        "fld9vFGOl3eYS17cL": to,
        "fldcZU1F2CID72sB6": cc,
        "fldlMx3pfsjpaNzgK": subject,
        "fldh8NbMPS2OxvPYD": body
    });
    console.log("Created an email record ", recordId);
}

function splitEmails(emailList) {

    let emails = emailList.split(',').map(email => email.trim());
    // Get the first email
    let firstEmail = emails[0];
    // Get the rest of the emails as a comma-separated string
    let restEmails = emails.slice(1).join(', ');

    return [firstEmail, restEmails];
}

