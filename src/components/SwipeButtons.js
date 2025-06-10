// src/components/SwipeButtons.js
import React from 'react';
import { XMarkIcon, HeartIcon } from '@heroicons/react/24/solid';

const SwipeButtons = ({ onSwipe }) => {
    return (
        <div className="flex justify-center items-center gap-8 mt-6">
            <button 
                onClick={() => onSwipe('left')}
                className="bg-white rounded-full p-4 shadow-lg hover:bg-gray-100 transition duration-200"
            >
                <XMarkIcon className="h-10 w-10 text-red-500" />
            </button>
            <button 
                onClick={() => onSwipe('right')}
                className="bg-white rounded-full p-4 shadow-lg hover:bg-gray-100 transition duration-200"
            >
                <HeartIcon className="h-10 w-10 text-teal-400" />
            </button>
        </div>
    );
};

export default SwipeButtons;
