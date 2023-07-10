import React from 'react'
import PropTypes from 'prop-types'
import {
    createBrowserRouter,
    RouterProvider,
    Route,
    NavLink,
    Router,
    Routes,
    BrowserRouter
  } from "react-router-dom";

export default function Navbar(props) {
  return (
    <>
      <nav className="navbar navbar-expand-lg bg-light bg-gradient">
        <div className="container-fluid">
          <a className="navbar-brand" href="#">
            <img className='m-2' src='https://upload.wikimedia.org/wikipedia/commons/6/67/Microsoft_To-Do_icon.png' width="30px"/>
            <span className='fw-bold'>{props.title}</span>
          </a>
          <button className="navbar-toggler" type="button">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarSupportedContent">
            <ul className="navbar-nav mx-auto mb-2 mb-lg-0 ">
              <li className="nav-item">
                <NavLink to="/" className={({ isActive, isPending }) =>
                  isActive ? "nav-link active" : "nav-link"
                }>Home</NavLink>
              </li>
              <li className="nav-item">
              <NavLink to="/pricing" className={({ isActive, isPending }) =>
                  isActive ? "nav-link active" : "nav-link"
                }>API Reference</NavLink>
              </li>
            </ul>
              { props.button ? <a className="btn btn-outline-dark" href='https://github.com/AdityaGirdhar/Focus' target='_blank'>Contribute!</a> : ""}
          </div>
        </div>
      </nav>
    </>
  )
}

Navbar.defaultProps = {
    title: "Default Title",
    button: true
}

Navbar.propTypes = {
    title: PropTypes.string,
    button: PropTypes.bool
}
