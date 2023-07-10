import React from 'react'

export default function TodoItem({task, onDelete, setData}) {
  const editModal = () => {
    let newTitle = prompt('Enter new title', task.title)
    let newDesc = prompt('Enter new description', task.desc)

    try {
			fetch('/update/'+task.sno, {
				method: "POST",
				body: JSON.stringify({
					title: newTitle,
					desc: newDesc
				}),
				headers: {
					'Content-Type': 'application/json'
				}
			})
			.then(() => {
        fetch('/show').then(
          res => res.json()
        ).then(data => {
          setData(data)
        })
      })
		} catch(err) {
			console.log(err);
		}
  }
  return (
    <>
    <div className='px-5 py-1 mw-100 d-flex justify-content-between my-4'>
        <div className='h-100'>
            <h4>{task.title}</h4>
            <p>{task.desc}</p>
            <p>{task.date}</p>
        </div>
        <div>
            <button onClick={() => editModal(task.sno)} className="me-auto btn btn-outline-light my-2 py-2 mx-1" aria-label="Close">✏️</button>
            <button onClick={() => onDelete(task.sno)} className="me-auto btn btn-outline-light my-2 py-2 mx-1" aria-label="Close">✅</button>
        </div>
    </div>
        <hr style={{'width': '90%', 'margin': 'auto'}}/>
    </>
  )
}