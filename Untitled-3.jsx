import React from 'react';
import ReactDOM from 'react-dom';

class App extends React.Component {
	
	onInputChange(event) {
		console.log(event.target.value);
	}
	
	render() {
		return (
			<div>
				<form>
					<label>Enter text</label>
					<input type="text"
						onChange={this.onInputChange}/>
				</form>
			</div>
		);
	}
}

ReactDOM.render(<App />,
			document.querySelector('#root'));
