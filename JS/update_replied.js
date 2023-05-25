let link_table = base.getTable("tbl8NAwDIqxcLasZL");
let email_queue_table = base.getTable("tblJaDA1FVHJIbx3b");
let inputConfig = input.config();
let email_id = inputConfig.email_id[0] ?? ''
let date = inputConfig.date;
let gmail_id = inputConfig.gmail_id
if(email_id){
    let records_to_update = []
    let link = await link_table.selectRecordAsync(email_id)
    let emails = link ? link.getCellValue("fldr3n17WgLEs6yp5") : null;
    let total_emails = emails?.length ?? null
    if (total_emails){
        emails.forEach(email =>{
            records_to_update.push({
                id: email,
                fields:{
                    "fldeoNVjJpbMNBv8d": {name: "Sequence Replied"}
                }
            })
        })
    }
    if(link?.id){
        await link_table.updateRecordAsync(link.id,{"fldbtSyNjnyorTPvb": date})
    }
    if(records_to_update?.length){
        await email_queue_table.updateRecordsAsync(records_to_update)
    }

}else{
    console.warn(`No email found for this gmail id ${gmail_id}`)
}
