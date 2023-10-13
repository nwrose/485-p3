import React, { useState, useEffect } from "react";
import PropTypes, { array } from "prop-types";
import Comment from "./comment"

export default function postComments({ commentsInfo }){ 

    // Render the comments individually
    
    return (
        <div id="comments">
            {console.log('Rendering the posts comments!')}
            {commentsInfo.map((comment) => <Comment key={comment.commentid} commentInfo={comment}/> )}
            <p id ="newComment">
                NEW COMMENT BUTTON
            </p>
        </div>
        );
}
postComments.propTypes = {
    commentsInfo: PropTypes.array.isRequired,
  };

