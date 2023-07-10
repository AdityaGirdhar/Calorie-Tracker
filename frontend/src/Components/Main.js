import React, { useEffect, useState } from 'react'
import AddTodo from './AddTodo'
import TodoItem from './TodoItem'

export default function Main() {

  const [data, setData] = useState([{}])

	useEffect(() => {
		fetch('/show').then(
			res => res.json()
		).then(data => {
			setData(data)
		})
	}, [])

  const onDelete = (sno) =>  {
    fetch('/delete/'+sno).then(() => {
    fetch('/show').then(
			res => res.json()
		).then(data => {
			setData(data)
		})
  })}

  return (
    <div className='container-sm mt-5 p-4 pb-4'>
        <h3 className='text-center mb-4'>Welcome, here are your tasks for today.</h3>
        <AddTodo setData={setData}/>
        <br/>
        <div className='d-flex flex-column flex-column-reverse'>
        {typeof data.tasks === 'undefined' ? (<center>Loading...</center>) :
        ( data.tasks.length === 0 ? (<div className="alert alert-secondary" role="alert">
                                        You're all caught up. Add another task now!
                                     </div>) :
          (data.tasks.map((task) => {
            return (<TodoItem
                      task={task}
                      key={task.sno}
                      onDelete={onDelete}
                      setData={setData}
                    />)
          })))
        }
        </div>
        <div className='m-5'>
            <br/>
            <br/>
        </div>
    </div>
  )
}