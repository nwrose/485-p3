import React, { useState, useEffect } from "react";
import PropTypes, { array } from "prop-types";
import Comment from "./comment"

export default function postComments({ commentsInfo, makeComment, setCommentText, deleteComment }){ 

    // Render the comments individually
    
    return (
        <div id="comments">
            {console.log('Rendering the posts comments!')}
            {commentsInfo.map((comment) => <Comment key={comment.commentid} commentInfo={comment} deleteComment={deleteComment}/> )}
            
            <form onSubmit={makeComment} data-testid="comment-form">
                <input 
                name="newComment"
                type = "text"
                placeholder = "Make New Comment"
                onChange={(e) => setCommentText(e.target.value)}
                />
            </form>
        </div>
        );
}
postComments.propTypes = {
    commentsInfo: PropTypes.array.isRequired,
    makeComment: PropTypes.func.isRequired,
    setCommentText: PropTypes.func.isRequired,
    deleteComment: PropTypes.func.isRequired,
  };

