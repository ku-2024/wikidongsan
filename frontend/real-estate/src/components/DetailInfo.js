import React, { useState } from "react";
import "../App.css"

const DetailInfo = ({ title, info, comment, id, icon }) => {
  // 토글 상태 관리
  const [isTextVisible, setIsTextVisible] = useState(false);

  const handleToggle = () => {
    setIsTextVisible((prev) => !prev); // 토글 상태 변경
  };

  return (
    <div
      id={id}
      title={title}
      className="mb-6 bg-slate-100 rounded-2xl p-8 border shadow-md"
    >
      
      
        <h1 className="flex justfy-start gap-3 items-center font-bold text-2xl py-2">
          {icon}
          {title}
        </h1>
          
      
      <p className="text-lg">{info || "정보를 수집하고 있는 아파트입니다"}</p>
      <div className="flex justify-end ">
        {/* 토글 버튼 */}
        <button
            onClick={handleToggle}
          >
            {isTextVisible ? <svg class="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
  <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m16 17-4-4-4 4m8-6-4-4-4 4"/>
</svg>
 : <svg class="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
  <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m8 7 4 4 4-4m-8 6 4 4 4-4"/>
</svg>

}
          </button>
      </div>
        
    
      

      {/* 토글 상태에 따라 보여지는 텍스트 */}
      {isTextVisible && (
        <div className="mt-10 flex justify-between gap-5">
          <div className="max-h-[45vh] overflow-y-auto w-[40vw]  rounded-lg ">
            <ul>
              <div className=" mb-5 rounded-lg bg-blue-100 p-3">
                {comment?.[3] || ""}
              </div>
              <div className=" mb-5 rounded-lg bg-blue-100 p-3">
                {comment?.[4] || ""}
              </div>
              <div className="mb-5 rounded-lg bg-blue-100 p-3">
                {comment?.[5] || ""}
              </div>
            </ul>
          </div>

          <div className="max-h-[45vh] overflow-y-auto w-[40vw]">
            <ul>
              <div className=" mb-5 rounded-lg bg-red-100 p-3">
                {comment?.[0] || ""}
              </div>
              <div className=" mb-5 rounded-lg bg-red-100 p-3">
              {comment?.[1] || ""}
              </div>
              <div className=" mb-5 rounded-lg bg-red-100 p-3">
              {comment?.[2] || ""} 
              </div>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default DetailInfo;
