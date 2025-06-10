# june-and-july

Of course! Building a full-stack dating app is a significant project, but we can create a comprehensive and high-quality blueprint for "June & July". This guide will provide the complete code structure, key component implementations, and the logic for your unique public ratio feature.

Given your requirements—popular, Python-compatible, and modern—the best tech stack is:

*   **Backend:** **Django** with **Django REST Framework (DRF)**. It's robust, secure, "batteries-included," and the industry standard for building powerful APIs with Python.
*   **Frontend:** **React**. It's the most popular frontend library, with a massive ecosystem perfect for creating a dynamic, component-based UI like a dating app.
*   **Database:** **PostgreSQL**. The best all-around, open-source relational database for serious projects. (We'll use SQLite for easy local setup).
*   **Styling:** **Tailwind CSS**. A utility-first CSS framework that is perfect for rapidly building beautiful, custom, and responsive designs like Hinge or Bumble without writing custom CSS files.

Let's design and build "June & July".

---

### **Part 1: Backend with Django & DRF**

The backend will handle user data, authentication, swiping logic, matching, and calculating our unique public ratios.

#### **1. Project Setup**

```bash
# 1. Set up a project directory
mkdir june-and-july
cd june-and-july

# 2. Set up Python virtual environment
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

# 3. Install Django and required packages
pip install django djangorestframework django-cors-headers Pillow

# 4. Start the Django project and an app for our core logic
django-admin startproject backend
cd backend
python manage.py startapp api
```

In `backend/settings.py`, add `rest_framework`, `api`, and `corsheaders` to `INSTALLED_APPS` and configure CORS to allow your frontend to connect.

```python
# backend/settings.py

INSTALLED_APPS = [
    # ...
    'rest_framework',
    'api',
    'corsheaders',
]

MIDDLEWARE = [
    # ...
    'corsheaders.middleware.CorsMiddleware', # Add this
    'django.middleware.common.CommonMiddleware',
    # ...
]

# Allow all origins for development. In production, restrict this to your domain.
CORS_ALLOW_ALL_ORIGINS = True
```

#### **2. Database Models (`api/models.py`)**

This is the heart of our app's data structure. The magic for your ratio feature happens here using `@property` decorators, which create dynamically calculated fields.

```python
# api/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Count, Q

class User(AbstractUser):
    # Add any additional user fields if needed, e.g., date_of_birth
    date_of_birth = models.DateField(null=True, blank=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    # Location, preferences etc. would go here

    def __str__(self):
        return self.user.username

    @property
    def swipe_ratio(self):
        """Calculates Right Swipes / Total Swipes Sent."""
        swipes_sent = self.user.sent_swipes.all()
        total_sent = swipes_sent.count()
        if total_sent == 0:
            return None # Or 0.0, depending on how you want to display it

        right_swipes_sent = swipes_sent.filter(direction='right').count()
        return round((right_swipes_sent / total_sent) * 100)

    @property
    def acceptance_ratio(self):
        """Calculates (Matches / Right Swipes Received) * 100."""
        right_swipes_received = self.user.received_swipes.filter(direction='right')
        total_received = right_swipes_received.count()
        if total_received == 0:
            return None # Or 0.0

        # A match is formed when the other user also swiped right.
        # We find how many of the people who swiped right on us, we also swiped right on.
        accepted_swipes = 0
        for swipe in right_swipes_received:
            # Check if WE swiped right on the person who swiped right on US
            if Swipe.objects.filter(swiper=self.user, swiped=swipe.swiper, direction='right').exists():
                accepted_swipes += 1

        return round((accepted_swipes / total_received) * 100)


class Photo(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='profile_photos/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

class Swipe(models.Model):
    DIRECTIONS = (('left', 'Left'), ('right', 'Right'))
    swiper = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_swipes')
    swiped = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_swipes')
    direction = models.CharField(max_length=5, choices=DIRECTIONS)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('swiper', 'swiped') # A user can only swipe on another user once

class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches2')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

# After defining models, run migrations
# python manage.py makemigrations
# python manage.py migrate
```

#### **3. API Serializers (`api/serializers.py`)**

Serializers convert our complex model data into JSON that the frontend can understand.

```python
# api/serializers.py

from rest_framework import serializers
from .models import User, Profile, Photo

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['image', 'order']

class ProfileSerializer(serializers.ModelSerializer):
    # Make the @property fields from the model available in the API
    swipe_ratio = serializers.IntegerField(read_only=True)
    acceptance_ratio = serializers.IntegerField(read_only=True)
    photos = PhotoSerializer(many=True, read_only=True)
    
    # Get user's first name and age
    first_name = serializers.CharField(source='user.first_name')
    # age = serializers.SerializerMethodField() # You would calculate age from date_of_birth

    class Meta:
        model = Profile
        fields = [
            'id', 'first_name', 'bio', 'job_title', 'company', 
            'photos', 'swipe_ratio', 'acceptance_ratio'
        ]

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'profile']
```

#### **4. API Views (`api/views.py`)**

These are the endpoints for getting profiles and performing swipes.

```python
# api/views.py

from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Profile, Swipe, Match, User
from .serializers import ProfileSerializer

class ProfileListView(generics.ListAPIView):
    """
    API endpoint to get a "deck" of potential matches.
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Exclude users we've already swiped on and ourself
        swiped_user_ids = Swipe.objects.filter(swiper=user).values_list('swiped_id', flat=True)
        return Profile.objects.exclude(user=user).exclude(user_id__in=swiped_user_ids)


class SwipeView(views.APIView):
    """
    API endpoint to record a swipe and check for a match.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        swiper = request.user
        swiped_id = request.data.get('swiped_id')
        direction = request.data.get('direction')

        if direction not in ['left', 'right']:
            return Response({'error': 'Invalid direction'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            swiped_user = User.objects.get(id=swiped_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create the swipe
        swipe, created = Swipe.objects.get_or_create(
            swiper=swiper,
            swiped=swiped_user,
            defaults={'direction': direction}
        )

        if not created: # If swipe already existed
            return Response({'message': 'Already swiped on this user'}, status=status.HTTP_200_OK)

        # Check for a match if the swipe was 'right'
        match_made = False
        if direction == 'right':
            # Check if the other user has swiped right on us
            if Swipe.objects.filter(swiper=swiped_user, swiped=swiper, direction='right').exists():
                Match.objects.create(user1=swiper, user2=swiped_user)
                match_made = True

        return Response({
            'status': 'swipe recorded',
            'match_made': match_made
        }, status=status.HTTP_201_CREATED)
```

#### **5. API URLs (`api/urls.py` and `backend/urls.py`)**

Wire up the views to URL endpoints.

```python
# api/urls.py
from django.urls import path
from .views import ProfileListView, SwipeView

urlpatterns = [
    path('profiles/', ProfileListView.as_view(), name='profile-list'),
    path('swipe/', SwipeView.as_view(), name='swipe'),
    # Add auth, match list, and chat endpoints here
]

# backend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
```

---

### **Part 2: Frontend with React & Tailwind CSS**

The frontend creates the "beautiful aesthetic" with rounded cards and displays all the data from our API.

#### **1. Project Setup**

```bash
# In your root 'june-and-july' directory (outside 'backend')
npx create-react-app frontend
cd frontend

# Install Tailwind CSS and other necessary packages
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install axios for API calls and react-router for navigation
npm install axios react-router-dom
```

Configure `tailwind.config.js` to scan your React components for class names.

```js
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Add the Tailwind directives to `src/index.css`.

```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

#### **2. Main Swiping Component (`src/components/Dashboard.js`)**

This is the main screen where users see profiles and swipe.

```jsx
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
```

#### **3. The Profile Card Component (`src/components/ProfileCard.js`)**

This component displays the user's info, including our custom ratios, with the Hinge/Bumble aesthetic.

```jsx
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
```

#### **4. Swipe Buttons Component (`src/components/SwipeButtons.js`)**

Clean, rounded buttons for the actions.

```jsx
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
```

#### **5. Putting it all together (`src/App.js`)**

```jsx
// src/App.js
import React from 'react';
import Dashboard from './components/Dashboard';

function App() {
    return (
        <div>
            {/* You would have a router here for login/registration/dashboard */}
            <Dashboard />
        </div>
    );
}

export default App;
```

### **Next Steps & Further Implementation**

This code provides a strong, working foundation. To make this a complete, production-ready app, you would need to:

1.  **Authentication:** Implement JWT (JSON Web Token) authentication. `dj-rest-auth` is a great Django package for this. Your React app would store the token and send it with every API request.
2.  **Photo Uploads:** The `Photo` model is ready. You'll need an endpoint to handle file uploads and configure Django to serve media files or, preferably, upload them to a cloud storage service like Amazon S3.
3.  **Real-time Chat:** For messaging between matches, you'll need WebSockets. Django Channels is the standard way to add WebSocket support to a Django application.
4.  **Geolocation:** Add location fields (latitude, longitude) to the `Profile` model and use them to find nearby users.
5.  **State Management:** For a larger React app, use a state management library like **Zustand** or **Redux Toolkit** to manage user authentication state, matches, and messages globally.
6.  **Deployment:** Deploy the Django backend (e.g., on Heroku or AWS) and the React frontend (e.g., on Vercel or Netlify).
7.  **Refined Matching Algorithm:** The current `ProfileListView` is basic. You could improve it based on user preferences, location, age, etc.
8.  **UI/UX Polish:** Add animations for card swipes (`framer-motion` is great for this in React) and create screens for user profiles, settings, and the match list.
