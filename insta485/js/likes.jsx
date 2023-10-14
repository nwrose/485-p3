import React, { useState, useEffect } from "react";
import PropTypes, { object } from "prop-types";


export default function Likes({ numLikes, toggleLike, likeStatus }){
    
    let singular = numLikes === 1
    return (
        <div id="likes">
            <div id = "button">
                <button data-testid="like-unlike-button" onClick={toggleLike}>{likeStatus ? 'unlike' : 'like'}</button>
            </div>
            {numLikes} <span>{singular ? 'like' : 'likes'}</span>
        </div>
        );
}
Likes.propTypes = {
    numLikes: PropTypes.number.isRequired,
    toggleLike: PropTypes.func.isRequired,
    likeStatus: PropTypes.bool.isRequired,
  };

