const editorContainer = document.getElementById('new-reply');

document.querySelectorAll('.replies-container, .post-container').forEach(container => {
    container.addEventListener('click', function(event) {

        if (event.target.classList.contains('report-button')) {
            event.preventDefault();
            const button = event.target;
            const postId = button.getAttribute('data-post-id');
            const replyId = button.getAttribute('data-reply-id');
            const replyAuthor = button.getAttribute('data-reply-user');

            console.log(postId, replyId, replyAuthor);
        }

        if(event.target.classList.contains('like-button')) {
            event.preventDefault();
            const button = event.target;
            const postId = button.getAttribute('data-post-id');
            const replyId = button.getAttribute('data-reply-id');
            const replyAuthor = button.getAttribute('data-reply-user');
            
            $.ajax({
                type: 'POST',
                url: likePostURL,
                data: {
                    'csrfmiddlewaretoken': csrfToken,
                    'entity_id': postId != null ? postId : replyId,
                    'entity_type': postId != null ? 'post' : 'reply',
                },
                success: function (data) {
                    if (data.success) {
                        const container = postId != null ? '.post-container' : '.reply-container';
                        const postContainer = button.closest(container);
                        const likeCountElement = postContainer.querySelector('.like-post-count');
                        if (likeCountElement) {
                            likeCountElement.textContent = data.like_count;
                        }
                
                        button.textContent = data.is_liked ? 'Liked' : 'Like';
                    }
                }
            });
        }

        if (event.target.classList.contains('reply-button')) {
            event.preventDefault();
            const button = event.target;
            const postId = button.getAttribute('data-post-id');
            const replyId = button.getAttribute('data-reply-id');
            const replyAuthor = button.getAttribute('data-reply-user');
    
            $.ajax({
                type: 'GET',
                url: getPostContentURL,
                data: {
                    'csrfmiddlewaretoken': csrfToken,
                    'entity_id': postId != null ? postId : replyId,
                    'entity_type': postId != null ? 'post' : 'reply',
                },
                success: function (data) {
                    if (data.success) {
                        const mainEditor = window.watchdog.editor;
                        const currentData = mainEditor.getData();
                        const replyBlock = `<p><blockquote><code class="ck-code_selected"><strong>Replying to ${replyAuthor}:</strong></code><br>${data.content}</blockquote></p>`;
                        const combinedData = currentData + replyBlock;
                        mainEditor.setData(combinedData);
                    }
                }
            });
            editorContainer.scrollIntoView({behavior: 'smooth'});
        }
    });
});

if(!isPostLocked){
    console.log(isPostLocked);
    document.getElementById('btn-submit-post').addEventListener('click', () => {
        var editor = window.watchdog.editor;
        if (editor.getData().length == 0) {
            showError('Post cannot be empty.');
            return;
        }
    
        document.getElementById('submit-post-modal').showModal();
    });

    document.getElementById('btn-submit-post-modal-yes').addEventListener('click', () => {
        var editor = window.watchdog.editor;
        var postData = editor.getData();
    
        $.ajax({
            type: 'POST',
            url: submitReplyURL.replace('0', postID),
            data: {
                'csrfmiddlewaretoken': csrfToken,
                'post_id': postID,
                'content': postData,
            },
            success: function (data) {
                if (data.success) {
                    var membershipHtml = '';
                    data.reply.author.memberships.forEach(function(membership) {
                        membershipHtml += `<kbd class="kbd kbd-sm" style="${membership.style}">${membership.name}</kbd>&nbsp;`;
                    });
    
                    var newReply = `
                        <div class="row row-editor mt-2 reply-container">
                            <div class="editor-container">
                                <div class="p-3 mt-2 border border-gray-800 author-panel">
                                    <div class="flex items-center space-x-4">
                                        <div class="avatar ml-2">
                                            <div class="w-24 rounded-full ring ring-offset-base-100 ring-offset-2" style="--tw-ring-color: ${data.reply.author.color};">
                                                <img src="${data.reply.author.profile_pic}" alt="${data.reply.author.name}"/>
                                            </div>
                                        </div>
                                        <div>
                                            <div class="text-white font-bold">
                                                ${data.reply.author.name_with_color}<br>
                                                ${membershipHtml}
                                            </div>
                                        </div>
                                    </div>
                                </div> 
                                <div class="ck-content-border">
                                    <div class="ck-content" id="reply-content">
                                        ${data.reply.content}
                                    </div>
                                </div>
                                <div id="date-posted" class="flex justify-between items-center">
                                    <div class="text-xs py-2">
                                        ${data.reply.created_at}
                                        ·
                                        <span class="mr-2">Liked by <span class="like-post-count">0</span> people</span>
                                    </div>
                                    <div class="text-end mr-2"> 
                                        <div>
                                            <a class="link link-primary text-orange-500 no-underline edit-button ml-2" data-post-id="{{ post.id }}" data-reply-user="{{ post.author.name }}">
                                                Edit
                                            </a>
                                            ·
                                            <button class="link link-primary text-orange-500 no-underline report-button" data-reply-id="${data.reply.id}" data-reply-user="${data.reply.author.name}">
                                                Report
                                            </button>
                                            ·
                                            <button class="link link-primary text-orange-500 no-underline like-button" data-reply-id="${data.reply.id}" data-reply-user="${data.reply.author.name}">
                                                Like
                                            </button>
                                            ·
                                            <button class="link link-primary text-orange-500 no-underline reply-button" data-reply-id="${data.reply.id}" data-reply-user="${data.reply.author.name}">
                                                Reply
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
    
                    document.querySelector('.replies-container').innerHTML += newReply;
                    editor.setData('');
                }
                else{
                    showError(data.message);
                }
            }
        });
    });
}