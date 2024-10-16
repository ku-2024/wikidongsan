import React, { useEffect, useRef } from 'react';
import ApexCharts from "apexcharts";

const Chart = ({apt_code, sq, avg_price, top_avg_price, bottom_avg_price}) => {


    const options = {
        series: [
          {
            name: "전체 평균",
            color: "#31C48D",
            data: [avg_price],
          },
          {
            name: "상위 30% 층 평균",
            data: [top_avg_price],
            color: "#F05252",
          },
          {
            name: "하위 30% 층 평균",
            data: [bottom_avg_price],
            color: "#F05252",
          }
        ],
        chart: {
          sparkline: {
            enabled: false,
          },
          type: "bar",
          width: "100%",
          height: 100,
          toolbar: {
            show: false,
          }
        },
        fill: {
          opacity: 1,
        },
        plotOptions: {
          bar: {
            horizontal: true,
            columnWidth: "100%",
            borderRadiusApplication: "end",
            borderRadius: 6,
            dataLabels: {
              position: "top",
            },
          },
        },
        legend: {
          show: true,
          position: "bottom",
        },
        dataLabels: {
          enabled: false,
        },
        tooltip: {
          shared: true,
          intersect: false,
          formatter: function (value) {
            return "₩" + value
          }
        },
        xaxis: {
          labels: {
            show: true,
            style: {
              fontFamily: "Inter, sans-serif",
              cssClass: 'text-xs font-normal fill-gray-500 dark:fill-gray-400'
            },
            formatter: function(value) {
              return "₩" + value
            }
          },
          categories: ["Price"],
          axisTicks: {
            show: false,
          },
          axisBorder: {
            show: false,
          },
        },
        yaxis: {
          labels: {
            show: true,
            style: {
              fontFamily: "Inter, sans-serif",
              cssClass: 'text-xs font-normal fill-gray-500 dark:fill-gray-400'
            }
          }
        },
        grid: {
          show: true,
          strokeDashArray: 4,
          padding: {
            left: 2,
            right: 2,
            top: -20
          },
        },
        fill: {
          opacity: 1,
        }
      }
      
    const chartsBox=document.getElementById(`${sq}`);
    // console.log(chartsBox);
    
    // if(chartsBox.getElementById("bar-chart") && typeof ApexCharts !== 'undefined') {
    //     const chart = new ApexCharts(chartsBox.getElementById("bar-chart"), options);
    //     chart.render();
    // }
    // console.log(chartsBox);
    //   const charts=chartsBox.getElementById(".bar-chart")
    //   console.log(charts)
    //   if(charts.length>0 && typeof ApexCharts !== 'undefined') {
    //     charts.forEach((chartElement) => {
    //         const chart = new ApexCharts(chartElement, options);
    //         chart.render();
    //       });
    //   }

    // if(document.getElementsByClassName(".bar-chart") && typeof ApexCharts !== 'undefined') {
    //     const chart = new ApexCharts(document.getElementsByClassName(".bar-chart"), options);
    //     chart.render();
    //   }


  return (
    
<div class="w-full bg-white rounded-lg shadow dark:bg-gray-800 p-4 md:p-6">
  <div class="flex justify-between border-gray-200 border-b dark:border-gray-700 pb-3">
    <dl>
      {/* <dt class="text-base font-normal text-gray-500 dark:text-gray-400 pb-1">Profit</dt> */}
      <dd class="leading-none text-3xl font-bold text-gray-900 dark:text-white">{sq}평</dd>
    </dl>
    <div>
      {/* <span class="bg-green-100 text-green-800 text-xs font-medium inline-flex items-center px-2.5 py-1 rounded-md dark:bg-green-900 dark:text-green-300">
        <svg class="w-2.5 h-2.5 me-1.5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 14">
          <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13V1m0 0L1 5m4-4 4 4"/>
        </svg>
        Profit rate 23.5%
      </span> */}
    </div>
  </div>

  {/* <div class="grid grid-cols-2 py-3">
    <dl>
      <dt class="text-base font-normal text-gray-500 dark:text-gray-400 pb-1">Income</dt>
      <dd class="leading-none text-xl font-bold text-green-500 dark:text-green-400">$23,635</dd>
    </dl>
    <dl>
      <dt class="text-base font-normal text-gray-500 dark:text-gray-400 pb-1">Expense</dt>
      <dd class="leading-none text-xl font-bold text-red-600 dark:text-red-500">-$18,230</dd>
    </dl>
  </div> */}
    <div id={sq}>
        <div id="bar-chart"></div>
    </div>
  
    <div class="grid grid-cols-1 items-center border-gray-200 border-t dark:border-gray-700 justify-between">
      <div class="flex justify-between items-center pt-5">
        
        {/* <a
          href="#"
          class="uppercase text-sm font-semibold inline-flex items-center rounded-lg text-blue-600 hover:text-blue-700 dark:hover:text-blue-500  hover:bg-gray-100 dark:hover:bg-gray-700 dark:focus:ring-gray-700 dark:border-gray-700 px-3 py-2">
          Revenue Report
          <svg class="w-2.5 h-2.5 ms-1.5 rtl:rotate-180" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 6 10">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 9 4-4-4-4"/>
          </svg>
        </a> */}
      </div>
    </div>
</div>

  )
  
}

export default Chart