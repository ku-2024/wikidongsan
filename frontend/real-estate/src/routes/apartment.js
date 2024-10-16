import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import DetailInfo from "../components/DetailInfo";
import { useParams } from "react-router-dom";
import {
  env,
  community,
  attribute,
  traffic,
  infra,
  school,
  sound,
  parking,
} from "../icon";
import ChatbotPopup from "../components/Chatbot";
import Chart from "../components/Chart";

const aptCodeList1=[
  "3ae33ebe", "79e9ff17", "93c2b21f", "1493f266", "4139b5cd", "a32c5888", "ac976530", "b1b4b365", "db1e18fb",  "b1850354","005dad14","0053d8de","0064fcce","00556f3e","00556387"
];

const Apartment = () => {
  const { apartmentId } = useParams();
  const [apt, setApt] = useState({});
  const [aptInfo, setAptInfo] = useState([]);
  const [summaries, setSummaries] = useState({});
  const [reviewsArray, setReviewsArray] = useState([]);
  const [commentsArray, setCommentsArray] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [infoResponse, dataResponse, summaryResponse, emotionResponse] = await Promise.all([
          fetch(`/get/apt_info/${apartmentId}`),
          fetch(`/getdata/${apartmentId}`),
          fetch(`/get/review-summary/${apartmentId}`),
          fetch(`/get/review-emotion/${apartmentId}`)
        ]);

        const infoData = await infoResponse.json();
        const data = await dataResponse.json();
        const summaryData = await summaryResponse.json();
        const emotionData = await emotionResponse.json();

        setAptInfo(infoData.data[0]);
        setApt(data);
        setSummaries(summaryData?.data ?? []);
        setReviewsArray(summaryData?.data?.reviews?.map(summary => summary.review) ?? []);

        const comments = emotionData?.data?.reviews?.map(summary => summary.review) ?? [];
        const chunkSize = 6;
        const chunkedArray = [];
        for (let i = 0; i < comments.length; i += chunkSize) {
          chunkedArray.push(comments.slice(i, i + chunkSize));
        }
        setCommentsArray(chunkedArray);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [apartmentId]);

  if (isLoading) return <div>로딩 중...</div>;
  if (error) return <div>에러 발생: {error}</div>;

  return (
    <div className="bg-slate-200">
      <div className="flex">
        <Sidebar />
        <div className="mt-3 p-[2%] mx-[2vw] ml-[18vw] w-[78vw]">
          <div className="flex rounded-2xl p-3">
            <div className="w-[100%]">
              <h1 className="font-bold text-4xl py-3 mb-4 flex">
                {apt?.data?.apt_name || "아파트 이름 없음"} 
              </h1>
              <div className="flex gap-10">
                <img
                  src={aptCodeList1.includes(apartmentId) ? `/image/${apartmentId}.jpeg` : "/noimage.jpg"}
                  className="w-[23vw] rounded-lg"
                  alt="Apartment Image"
                />
                <dl className="max-w-md text-gray-900 divide-y divide-gray-200 dark:text-white dark:divide-gray-700">
                  <div className="flex flex-col pb-3">
                    <dt className="mb-1 text-gray-500 md:text-lg dark:text-gray-400">주소</dt>
                    <dd className="text-lg font-semibold">{aptInfo.land_address}</dd>
                  </div>
                  <div className="flex flex-col py-3">
                    <dt className="mb-1 text-gray-500 md:text-lg dark:text-gray-400">세대수</dt>
                    <dd className="text-lg font-semibold">{aptInfo.total_households}</dd>
                  </div>
                  <div className="flex flex-col pt-3">
                    <dt className="mb-1 text-gray-500 md:text-lg dark:text-gray-400">완공일자</dt>
                    <dd className="text-lg font-semibold">{aptInfo.completion_date}</dd>
                  </div>
                  <div className="flex flex-col pt-3">
                    <dt className="mb-1 text-gray-500 md:text-lg dark:text-gray-400">시공사</dt>
                    <dd className="text-lg font-semibold">{aptInfo.construction_company}</dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="ml-[18vw] px-[2%] mx-[2vw]">
        <div className="flex flex-wrap justify-between mb-4">
          {apt?.data?.trades?.length > 0 ? (
            apt.data.trades.slice(0, 4).map((element, index) => (
              <div
                key={index}
                className="border bg-slate-100 shadow-md rounded-xl p-3 mr-5 mt-5 w-[36vw]"
                id={`${element.apt_sq}`}
              >
                <div className="flex justify-between border-gray-200 dark:border-gray-700 pb-3">
                  <dl>
                    <dd className="leading-none text-2xl font-bold text-gray-900 dark:text-white">{element.apt_sq}평</dd>
                  </dl>
                </div>
                <div>{element.avg_price}</div>
                <div>{element.top_avg_price}</div>
                <div>{element.bottom_avg_price}</div>
              </div>
            ))
          ) : (
            <div>No data available</div>
          )}
        </div>
        <DetailInfo id="A-env" title="환경(단지,조경)" info={reviewsArray[0]} comment={commentsArray[0]} icon={env} />
        <DetailInfo id="A-community" title="커뮤니티" info={reviewsArray[1]} comment={commentsArray[1]} icon={community} />
        <DetailInfo id="A-attribute" title="동별 특징" info={reviewsArray[2]} comment={commentsArray[2]} icon={attribute} />
        <DetailInfo id="A-infra" title="주변 상권" info={reviewsArray[3]} comment={commentsArray[3]} icon={infra} />
        <DetailInfo id="A-traffic" title="교통" info={reviewsArray[4]} comment={commentsArray[4]} icon={traffic} />
        <DetailInfo id="A-school" title="학군" info={reviewsArray[5]} comment={commentsArray[5]} icon={school} />
        <DetailInfo id="A-sound" title="소음" info={reviewsArray[6]} comment={commentsArray[6]} icon={sound} />
        <DetailInfo id="A-parking" title="주차" info={reviewsArray[7]} comment={commentsArray[7]} icon={parking} />
        <ChatbotPopup apt_code={apartmentId}/>
      </div>
    </div>
  );
};

export default Apartment;