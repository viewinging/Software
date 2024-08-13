import React, { useState } from 'react';
import './pad.css';

// Pad 컴포넌트 정의, onOpenPopup 함수는 부모 컴포넌트로부터 전달받음
function Pad({ onOpenPopup }) {
    // phoneNumber 상태 변수와 setPhoneNumber 상태 변경 함수 선언
    const [phoneNumber, setPhoneNumber] = useState('');

    // 버튼 클릭 핸들러 함수 정의
    const handleButtonClick = (value) => {
        // 전화번호 길이에 따라 하이픈 추가
        if (phoneNumber.length === 3 || phoneNumber.length === 8) {
            setPhoneNumber(phoneNumber + '-' + value);
        } else if (phoneNumber.length < 13) {
            setPhoneNumber(phoneNumber + value);
        }
    };

    // 삭제 버튼 클릭 핸들러 함수 정의
    const handleDelete = () => {
        // 마지막 문자 삭제
        setPhoneNumber(phoneNumber.slice(0, -1));
    };

    // 전화번호가 유효한지 체크 (길이가 13인지)
    const isPhoneNumberValid = phoneNumber.length === 13;

    function App() {
        const [nicknames, setNicknames] = useState([]);
    
        useEffect(() => {
            fetchNicknames();  // 컴포넌트가 처음 마운트될 때 닉네임 데이터를 가져오는 함수 호출
          }, []);
    
    //닉네임 데이터 가져오는 함수
    const fetchNicknames = () => {
        fetch('http://192.168.0.106:5000')
        .then(Response => Response.json()) //서버로부터 응답을 json형식으로 변환.
        .then(data => setNicknames(data))
        .catch(error => console.error('Error fetching data:', error));

    }

    return (
        <div className="pad">
            {/* SVG 요소로 디자인된 키패드 UI */}
            <svg width="438" height="612" viewBox="0 0 438 612" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g filter="url(#filter0_d_524_48)">
                    <rect x="10" y="6" width="418" height="592" rx="50" fill="white" />
                </g>
                {/* foreignObject를 사용하여 SVG 내에 HTML 콘텐츠 삽입 */}
                <foreignObject x="10" y="20" width="418" height="460">
                    {/* 전화번호 표시 영역 */}
                    <div className="phone-number-display">{phoneNumber}</div>
                    {/* 키패드 버튼들 */}
                    <div className="keypad">
                        {['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', '←'].map((key) => (
                            <button
                                key={key}
                                className="keypad-button"
                                onClick={() => key === '←' ? handleDelete() : key && handleButtonClick(key)}
                            >
                                {key}
                            </button>
                        ))}
                    </div>
                </foreignObject>
                <foreignObject x="10" y="480" width="418" height="100">
                    {/* 확인 버튼, 전화번호가 유효하지 않으면 비활성화 */}
                    <div className="button-container">
                        <button className="my-button" onClick={onOpenPopup} disabled={!isPhoneNumberValid}>확인</button>
                    </div>
                </foreignObject>
                {/* SVG 필터 정의 */}
                <defs>
                    <filter id="filter0_d_524_48" x="0" y="0" width="438" height="612" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
                        <feFlood floodOpacity="0" result="BackgroundImageFix" />
                        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha" />
                        <feOffset dy="4" />
                        <feGaussianBlur stdDeviation="5" />
                        <feComposite in2="hardAlpha" operator="out" />
                        <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.25 0" />
                        <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_524_48" />
                        <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_524_48" result="shape" />
                    </filter>
                </defs>
            </svg>
        </div>
    );
}

export default Pad;
