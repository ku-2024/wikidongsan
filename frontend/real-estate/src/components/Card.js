import React, { useEffect, useState } from "react";
import { useNavigate } from 'react-router-dom';

const aptCodeList1=[
  "3ae33ebe", "79e9ff17", "93c2b21f", "1493f266", "4139b5cd", "a32c5888", "ac976530", "b1b4b365", "db1e18fb",  "b1850354","005dad14","0053d8de","0064fcce","00556f3e","00556387"
];

const Card = ({ name, code, idx }) => {

  const navigate = useNavigate();
  const [randIndx,setRandIndx] = useState('');
  const [aptInfo, setAptInfo]=useState('');
  const [imgCode, setImgCode]=useState('');
  const [error, setError] = useState(null);
  const [aptImg,setAptImg]=useState('');

 

  useEffect(() => {
    const fetchData = async () => {
      // setIsLoading(true);
      setError(null);
      try {
        const [infoResponse] = await Promise.all([
          fetch(`/get/apt_info/${code}`),
        ]);

        const infoData = await infoResponse.json();

        setAptInfo(infoData.data[0]);

      } catch (err) {
        setError(err.message);
      } finally {
        // setIsLoading(false);
      }
    };

    fetchData();
  }, [code]);

  useEffect(() => {
    setImgCode(checkCodeList(code));
  }, [code]);

  const checkCodeList = (code) => {
    if (aptCodeList1.includes(code)) {
      setAptImg(`/image/${code}.jpeg`);
    } else {
      let keys = Object.keys(aptCodeList1[0]);
      let randomIndex = Math.floor(Math.random() * keys.length);
      setRandIndx(randomIndex)
      // return aptCodeList1[0][randomIndex];
      setAptImg(`/image/${aptCodeList1[idx]}.jpeg`)
    }
  };

  // console.log(name);
  // console.log(aptCodeList1[0]);
  // console.log(apartmentInfo);
  // console.log("db1e18fb" in aptCodeList1[0]);

  const handleReadMore = () => {
    // navigate(`/apartment/${code}`, { state: { apartmentInfo } });
    navigate(`/apartment/${code}/`)

  };


  
  return (
    <div className="max-w-sm border rounded-lg shadow bg-gray-800 border-gray-700">
      <a href="#">
        <img
          className="rounded-t-lg h-[55%] w-[100%] object-cover"
          src={aptImg}
          alt={name}
        />
      </a>

      <div className="px-5 pt-5">
        <h5 className="mb-2 text-2xl font-bold tracking-tight text-white">
          {name}
        </h5>
        <p className="font-normal text-gray-400">주소: {aptInfo.land_address}</p>
        <p className="font-normal text-gray-400">세대수: {aptInfo.total_households}</p>
        <p className="font-normal text-gray-400">
          완공일자: {aptInfo.completion_date}
        </p>

        <div className="flex justify-end">
        <button
          onClick={handleReadMore}
          className="inline-flex items-center px-3 py-2 text-sm font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
        >
            더 보기
        
            <svg
              className="rtl:rotate-180 w-3.5 h-3.5 ms-2"
              aria-hidden="true"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 14 10"
            >
              <path
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M1 5h12m0 0L9 1m4 4L9 9"
              />
            </svg>
            </button>
        </div>
      </div>
    </div>
  );
};

export default Card;
