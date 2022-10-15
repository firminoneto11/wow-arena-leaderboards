import { Fragment } from 'react';

import { Table } from './components/Table';

import './App.css';


export default function App() {

  return (
    <Fragment>
      <div className='flex justify-evenly'>
        <ul className="menu menu-horizontal bg-base-100 rounded-box p-2">
          <li><button className={`btn btn-primary rounded box btn-wide`}>2s</button></li>
          <li><button className={`btn rounded box btn-wide`}>3s</button></li>
          <li><button className={`btn btn-primary rounded box btn-wide`}>RBG</button></li>
        </ul>
      </div>
      <div className="artboard artboard-horizontal phone-6" style={{ margin: 'auto' }}>
        <Table />
      </div>
    </Fragment >
  );

}
