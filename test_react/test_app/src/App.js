// import React, { useState, useEffect } from 'react';

// function App() {
//   const [nicknames, setNicknames] = useState([]);

//   useEffect(() => {
//     fetchNicknames();  // 컴포넌트가 처음 마운트될 때 닉네임 데이터를 가져오는 함수 호출
//   }, []);

//   // 닉네임 데이터를 가져오는 함수
//   const fetchNicknames = () => {
//     fetch('http://192.168.0.106:5000')  
//       .then(response => response.json())
//       .then(data => setNicknames(data))
//       .catch(error => console.error('Error fetching data:', error));
//   };

//   // 버튼 클릭 시 닉네임 데이터를 다시 가져오도록 설정하는 함수
//   const handleClick = () => {
//     fetchNicknames();
//   };

//   return (
//     <div>
//       <h1>Nicknames from Flask API</h1>
//       <button onClick={handleClick}>Refresh Nicknames</button>
//       <ul>
//         {nicknames.map(nickname => (
//           <li key={nickname.id}>{nickname.name}</li>
//         ))}
//       </ul>
//     </div>
//   );
// }

// export default App;
