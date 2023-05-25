let link_table = base.getTable("tbl8NAwDIqxcLasZL");
let email_queue_table = base.getTable("tblJaDA1FVHJIbx3b");
let inputConfig = input.config();
let backlink_id = inputConfig.backlink_id[0] ?? '';
let email_id = inputConfig.email_id[0] ?? ''
let date = inputConfig.date;
let gmail_id = inputConfig.gmail_id;
let date_replied = inputConfig.date_replied;
if(email_id){
    let records_to_update = []
    let link = await link_table.selectRecordAsync(backlink_id)
    let emails = link ? link.getCellValue("fldr3n17WgLEs6yp5") : null;
    let total_emails = emails?.length ?? null;
    console.log(`total emails `,total_emails)
    if (total_emails){
        emails.forEach(email =>{
            if(email.id !== email_id){
                records_to_update.push({
                    id: email.id,
                    fields:{
                        "fldeoNVjJpbMNBv8d": {name: "Sequence Replied"}
                    }
                })
            }else{
                records_to_update.push({
                    id: email.id,
                    fields:{
                        "fldeoNVjJpbMNBv8d": {name: "Sequence Replied"},
                        "fldXg1AA6R8w8NoYg": date_replied
                    }
                })
            }

        })
    }
    if(link?.id){
        console.log(`uptading backlin ${link.name}`)
        await link_table.updateRecordAsync(link.id,{"fldbtSyNjnyorTPvb": date})
    }
    if(records_to_update?.length){
        console.log(`updating emails queue`, records_to_update)
        await email_queue_table.updateRecordsAsync(records_to_update)
    }

}else{
    console.warn(`No email found for this gmail id ${gmail_id}`)
}

