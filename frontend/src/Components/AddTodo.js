import React from 'react'
import { useState } from 'react'

export default function AddTodo( {setData} ) {
	const [title, setTitle] = useState("");
	const [desc, setDesc] = useState("");

	const handleSubmit = (e) => {
		e.preventDefault();
		if (title === "") {
			alert("Sorry, the title can't be empty. Please try again!")
			return
		}
		try {
			fetch('/', {
				method: "POST",
				body: JSON.stringify({
					title: title,
					desc: desc
				}),
				headers: {
					'Content-Type': 'application/json'
				}
			})
			.then(res => res.json())
			.then(data => {
				setData(data)
				setTitle("")
				setDesc("")
			})
		} catch(err) {
			console.log(err);
		}
	}
	
  return (
    <div className="shadow my-3 p-4 rounded">
		<h5 className='text-center pb-3'>Add new task</h5>
        <form onSubmit={handleSubmit}>
            <input
				type="text"
				value={title}
				className="form-control w-100 mb-2"
				id="title"
				name='title'
				placeholder="Water the plants..."
				onChange={(e)=>{setTitle(e.target.value)}}
			/>
            <input
				type="text"
				value={desc}
				className="form-control w-100 mt-3" 
				id="desc"
				name='desc'
				placeholder="I'll do my part in saving the planet..."
				onChange={(e)=>{setDesc(e.target.value)}}
			/>
			<div className="col text-center my-4">
            	<button type="submit" className="btn btn-primary mx-2">
					+ Add new task
				</button>
            	<button type="button" className="btn btn-danger mx-2">
					× Clear tasks
				</button>
            </div>
        </form>
    </div>
  )
}
