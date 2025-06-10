// src/components/ProfileCard.js
import React from 'react';

const RatioDisplay = ({ label, value, colorClass }) => {
    if (value === null || value === undefined) return null;
    return (
        <div className="text-center">
            <p className="text-sm text-gray-500">{label}</p>
            <p className={`text-2xl font-bold ${colorClass}`}>{value}%</p>
        </div>
    );
};

const ProfileCard = ({ profile }) => {
    return (
        <div className="absolute top-0 left-0 w-full h-full bg-white rounded-2xl shadow-xl overflow-hidden flex flex-col">
            {/* Image */}
            <div className="flex-grow bg-cover bg-center" style={{ backgroundImage: `url(${profile.photos[0]?.image || 'default_image_url.jpg'})` }}>
                {/* Gradient overlay for text */}
                <div className="w-full h-full flex flex-col justify-end p-6 bg-gradient-to-t from-black/60 to-transparent">
                    <h2 className="text-white text-3xl font-bold">{profile.first_name}, 28</h2>
                    <p className="text-white/90 text-lg">{profile.job_title}</p>
                </div>
            </div>

            {/* Info Section */}
            <div className="p-6">
                <p className="text-gray-700 mb-4">{profile.bio}</p>
                
                {/* --- PUBLIC RATIOS --- */}
                <div className="border-t border-gray-200 pt-4 flex justify-around">
                    <RatioDisplay 
                        label="Swipe Ratio"
                        value={profile.swipe_ratio}
                        colorClass="text-blue-500"
                    />
                    <RatioDisplay 
                        label="Acceptance Ratio"
                        value={profile.acceptance_ratio}
                        colorClass="text-green-500"
                    />
                </div>
            </div>
        </div>
    );
};

export default ProfileCard;
