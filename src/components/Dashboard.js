// src/components/Dashboard.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ProfileCard from './ProfileCard';
import SwipeButtons from './SwipeButtons';

// You would get this from your auth context/state management
const AUTH_TOKEN = 'your_jwt_token_here'; 
const API_URL = 'http://127.0.0.1:8000/api';

const Dashboard = () => {
    const [profiles, setProfiles] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);

    useEffect(() => {
        const fetchProfiles = async () => {
            try {
                const response = await axios.get(`${API_URL}/profiles/`, {
                    headers: { Authorization: `Bearer ${AUTH_TOKEN}` }
                });
                setProfiles(response.data);
            } catch (error) {
                console.error("Error fetching profiles:", error);
            }
        };
        fetchProfiles();
    }, []);

    const handleSwipe = async (direction) => {
        if (currentIndex >= profiles.length) return;

        const swipedId = profiles[currentIndex].id;

        try {
            await axios.post(`${API_URL}/swipe/`, 
                { swiped_id: swipedId, direction: direction },
                { headers: { Authorization: `Bearer ${AUTH_TOKEN}` } }
            );
            // Move to the next card
            setCurrentIndex(prevIndex => prevIndex + 1);
        } catch (error) {
            console.error("Error swiping:", error);
        }
    };

    const currentProfile = profiles.length > 0 && currentIndex < profiles.length 
        ? profiles[currentIndex] 
        : null;

    return (
        <div className="bg-gray-100 min-h-screen flex flex-col items-center justify-center p-4">
            <h1 className="text-4xl font-bold text-pink-500 mb-6">june & july</h1>
            <div className="relative w-full max-w-sm h-[600px]">
                {currentProfile ? (
                    <ProfileCard profile={currentProfile} />
                ) : (
                    <div className="flex items-center justify-center h-full bg-white rounded-2xl shadow-xl">
                        <p className="text-gray-500">No more profiles for now!</p>
                    </div>
                )}
            </div>
            {currentProfile && <SwipeButtons onSwipe={handleSwipe} />}
        </div>
    );
};

export default Dashboard;
