import React, { useState, useEffect } from "react";
import PropTypes, { array } from "prop-types";
import Post from "./post";
import InfiniteScroll from "react-infinite-scroll-component";

export default function Feed({ url }){
    const [postArr, setPostArr] = useState([]);
    const [pageNext, setPageNext] = useState("");
    useEffect(() => {
        let ignoreStaleRequest = false;

        function functFetch(){
            fetch(url, { credentials: "same-origin" })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                if (!ignoreStaleRequest) {
                    let posts = postArr;
                    setPostArr([...posts, ...data.results]);
                    setPageNext(data.next);
                }
            })
            .catch((error) => console.log(error));
        }
        
        //Call Rest API to get the list of posts on feed
        fetch(url, { credentials: "same-origin" })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                if (!ignoreStaleRequest) {
                    let posts = postArr;
                    setPostArr([...posts, ...data.results]);
                    setPageNext(data.next);
                }
            })
            .catch((error) => console.log(error));

        return () => {
            // Cleanup function --> refer to post.jsx desc
            //    for more info about ignoreStaleRequest
            ignoreStaleRequest = true;
        }
    }, [url]);

    //define postFunc
    function postFunc(post){
        return <Post key={post.postid} url={`/api/v1/posts/${post.postid}/`}/>
    }

    // Render the feed
    return (
        <div id="feed">
            <InfiniteScroll
            dataLength={postArr.length}
            next={bottomLoad}

            >
                {console.log('rendering the feed!')}
                {postArr.map((post) => postFunc(post) )}
            </InfiniteScroll>
        </div>
        );
}

Feed.propTypes = {
    url: PropTypes.string.isRequired,
  };
