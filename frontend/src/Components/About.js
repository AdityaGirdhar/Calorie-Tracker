import React, { useState, useEffect } from 'react'

export default function About() {
	const [data, setData] = useState([{}])

	useEffect(() => {
		fetch('/show').then(
			res => res.json()
		).then(data => {
			setData(data)
		})
	}, [])

	return (
		<div>
			{(typeof data.tasks === 'undefined') ? (
				<p>Loading...</p>
			) : (
				// <p>hello</p>
				data.tasks.map((task) => (
					<p key={task.sno}> {task.title} </p>
				))
			)}
		</div>
	)
}
