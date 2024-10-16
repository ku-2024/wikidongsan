import React from "react";

const Pagination = ({ totalPages, currentPage, handlePageChange }) => {
  const getPageNumbers = () => {
    const pageNumbers = [];
    if (totalPages <= 10) {
      // 10페이지 이하일 경우 모든 페이지 표시
      for (let i = 1; i <= totalPages; i++) {
        pageNumbers.push(i);
      }
    } else {
      // 10페이지 초과일 경우 현재 페이지 주변 페이지 표시
      let start = Math.max(1, currentPage - 4);
      let end = Math.min(totalPages, start + 9);

      if (end - start < 9) {
        start = Math.max(1, end - 9);
      }

      for (let i = start; i <= end; i++) {
        pageNumbers.push(i);
      }

      if (start > 1) {
        pageNumbers.unshift('...');
        pageNumbers.unshift(1);
      }
      if (end < totalPages) {
        pageNumbers.push('...');
        pageNumbers.push(totalPages);
      }
    }
    return pageNumbers;
  };

  const pageNumbers = getPageNumbers();

  return (
    <nav aria-label="Page navigation example">
      <ul className="inline-flex -space-x-px text-base h-10">
        <li>
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            className={`flex items-center justify-center px-4 h-10 ms-0 leading-tight border border-e-0 rounded-s-lg bg-gray-800 border-gray-700 text-gray-400 hover:bg-gray-700 hover:text-white`}
            disabled={currentPage === 1}
          >
            Previous
          </button>
        </li>

        {pageNumbers.map((page, index) => (
          <li key={index}>
            {page === '...' ? (
              <span className="flex items-center justify-center px-4 h-10 leading-tight bg-gray-800 text-gray-400">
                ...
              </span>
            ) : (
              <button
                onClick={() => handlePageChange(page)}
                className={`flex items-center justify-center px-4 h-10 leading-tight ${
                  currentPage === page
                    ? "hover:bg-blue-100 hover:text-blue-700 bg-gray-700 text-white"
                    : "bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white"
                }`}
              >
                {page}
              </button>
            )}
          </li>
        ))}

        <li>
          <button
            onClick={() => handlePageChange(currentPage + 1)}
            className={`flex items-center justify-center px-4 h-10 leading-tight border rounded-e-lg bg-gray-800 border-gray-700 text-gray-400 hover:bg-gray-700 hover:text-white`}
            disabled={currentPage === totalPages}
          >
            Next
          </button>
        </li>
      </ul>
    </nav>
  );
};

export default Pagination;