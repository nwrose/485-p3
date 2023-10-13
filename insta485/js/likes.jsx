import React, { useState, useEffect } from "react";
import PropTypes, { object } from "prop-types";


export default function Likes({ likesInfo, toggleLike }){ 
    
    let singular = likesInfo.numLikes === 1
    return (
        <div id="likes">
            <div id = "button">
                <button onClick={toggleLike}>{likeStatus ? 'unlike' : 'like'}</button>
            </div>
            {likesInfo['numLikes']} <span>{singular ? 'like' : 'likes'}</span>
        </div>
        );
}
Likes.propTypes = {
    likesInfo: PropTypes.object.isRequired,
    toggleLike: PropTypes.func.isRequired,
  };

